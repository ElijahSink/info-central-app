import { useState, useEffect } from 'react';
import { Responsive, WidthProvider } from 'react-grid-layout';
import { Plus, RefreshCw } from 'lucide-react';
import { Button } from './ui/button';
import { BlockCard } from './BlockCard';
import { AddBlockDialog } from './AddBlockDialog';
import { ApiService } from '../lib/api';
import { toast } from './ui/toaster';
import type { Block } from '../types';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';

const ResponsiveGridLayout = WidthProvider(Responsive);

export function Dashboard() {
  const [blocks, setBlocks] = useState<Block[]>([]);
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadBlocks();
  }, []);

  const loadBlocks = async () => {
    try {
      setIsLoading(true);
      const fetchedBlocks = await ApiService.getBlocks();
      setBlocks(fetchedBlocks);
    } catch (error) {
      console.error('Error loading blocks:', error);
      toast({
        variant: 'destructive',
        description: 'Failed to load blocks. Check if the backend is running.',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateBlock = async (userPrompt: string, title?: string) => {
    try {
      const newBlock = await ApiService.createBlock({
        user_prompt: userPrompt,
        title,
      });
      
      setBlocks(prev => [...prev, newBlock]);
      setIsAddDialogOpen(false);
      
      toast({
        variant: 'default',
        description: `Block "${newBlock.title}" created successfully!`,
      });
    } catch (error) {
      console.error('Error creating block:', error);
      toast({
        variant: 'destructive',
        description: 'Failed to create block. Please try again.',
      });
    }
  };

  const handleUpdateBlock = async (id: number, userPrompt: string) => {
    try {
      const updatedBlock = await ApiService.updateBlock(id, {
        user_prompt: userPrompt,
      });
      
      setBlocks(prev => prev.map(block => 
        block.id === id ? updatedBlock : block
      ));
      
      toast({
        variant: 'default',
        description: 'Block updated successfully!',
      });
    } catch (error) {
      console.error('Error updating block:', error);
      toast({
        variant: 'destructive',
        description: 'Failed to update block. Please try again.',
      });
    }
  };

  const handleDeleteBlock = async (id: number) => {
    try {
      await ApiService.deleteBlock(id);
      setBlocks(prev => prev.filter(block => block.id !== id));
      
      toast({
        variant: 'default',
        description: 'Block deleted successfully!',
      });
    } catch (error) {
      console.error('Error deleting block:', error);
      toast({
        variant: 'destructive',
        description: 'Failed to delete block. Please try again.',
      });
    }
  };

  const handleHealBlock = async (id: number) => {
    try {
      const healedBlock = await ApiService.healBlock(id);
      setBlocks(prev => prev.map(block => 
        block.id === id ? healedBlock : block
      ));
      
      toast({
        variant: 'default',
        description: 'Block healing attempted!',
      });
    } catch (error) {
      console.error('Error healing block:', error);
      toast({
        variant: 'destructive',
        description: 'Failed to heal block. Please try again.',
      });
    }
  };

  const handleLayoutChange = async (layout: any[]) => {
    // Update layout for all blocks
    for (const item of layout) {
      const blockId = parseInt(item.i);
      const layoutData = {
        x: item.x,
        y: item.y,
        w: item.w,
        h: item.h,
      };

      try {
        await ApiService.updateBlockLayout(blockId, { layout_data: layoutData });
        
        // Update local state
        setBlocks(prev => prev.map(block => 
          block.id === blockId 
            ? { ...block, layout_data: layoutData }
            : block
        ));
      } catch (error) {
        console.error('Error updating layout:', error);
      }
    }
  };

  // Convert blocks to grid layout format
  const layouts = {
    lg: blocks.map(block => ({
      i: block.id.toString(),
      x: block.layout_data.x,
      y: block.layout_data.y,
      w: block.layout_data.w,
      h: block.layout_data.h,
      minW: 2,
      minH: 2,
    }))
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin">
          <RefreshCw className="h-8 w-8" />
        </div>
        <span className="ml-2">Loading blocks...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Dashboard Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">Dashboard</h2>
          <p className="text-muted-foreground">
            {blocks.length} {blocks.length === 1 ? 'block' : 'blocks'} active
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={loadBlocks}
            disabled={isLoading}
          >
            <RefreshCw className="h-4 w-4 mr-1" />
            Refresh
          </Button>
          
          <Button
            onClick={() => setIsAddDialogOpen(true)}
            size="sm"
          >
            <Plus className="h-4 w-4 mr-1" />
            Add Block
          </Button>
        </div>
      </div>

      {/* Empty State */}
      {blocks.length === 0 ? (
        <div className="text-center py-12">
          <div className="mx-auto w-24 h-24 bg-muted rounded-full flex items-center justify-center mb-4">
            <Plus className="h-8 w-8 text-muted-foreground" />
          </div>
          <h3 className="text-lg font-medium mb-2">No blocks yet</h3>
          <p className="text-muted-foreground mb-4">
            Create your first AI-powered dashboard block by describing what you want to see.
          </p>
          <Button onClick={() => setIsAddDialogOpen(true)}>
            <Plus className="h-4 w-4 mr-1" />
            Add Your First Block
          </Button>
        </div>
      ) : (
        /* Grid Layout */
        <ResponsiveGridLayout
          className="layout"
          layouts={layouts}
          breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 }}
          cols={{ lg: 12, md: 10, sm: 6, xs: 4, xxs: 2 }}
          rowHeight={60}
          onLayoutChange={handleLayoutChange}
          draggableHandle=".drag-handle"
        >
          {blocks.map((block) => (
            <div key={block.id.toString()}>
              <BlockCard
                block={block}
                onUpdate={handleUpdateBlock}
                onDelete={handleDeleteBlock}
                onHeal={handleHealBlock}
              />
            </div>
          ))}
        </ResponsiveGridLayout>
      )}

      {/* Add Block Dialog */}
      <AddBlockDialog
        open={isAddDialogOpen}
        onOpenChange={setIsAddDialogOpen}
        onSubmit={handleCreateBlock}
      />
    </div>
  );
}