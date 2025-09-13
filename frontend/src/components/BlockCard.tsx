import { useState, useEffect } from 'react';
import { MoreVertical, RefreshCw, Edit, Trash2, AlertTriangle, Move } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from './ui/dialog';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { ApiService } from '../lib/api';
import { toast } from './ui/toaster';
import type { Block, BlockData } from '../types';

interface BlockCardProps {
  block: Block;
  onUpdate: (id: number, userPrompt: string) => void;
  onDelete: (id: number) => void;
  onHeal: (id: number) => void;
}

export function BlockCard({ block, onUpdate, onDelete, onHeal }: BlockCardProps) {
  const [blockData, setBlockData] = useState<BlockData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [editPrompt, setEditPrompt] = useState(block.user_prompt);
  const [generatedComponent, setGeneratedComponent] = useState<React.ComponentType | null>(null);

  useEffect(() => {
    loadBlockData();
  }, [block.id]);

  const loadBlockData = async () => {
    try {
      setIsLoading(true);
      const data = await ApiService.getBlockData(block.id);
      setBlockData(data);
    } catch (error) {
      console.error('Error loading block data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = async () => {
    try {
      setIsLoading(true);
      const data = await ApiService.refreshBlock(block.id);
      setBlockData(data);
      toast({
        variant: 'default',
        description: 'Block refreshed successfully!',
      });
    } catch (error) {
      console.error('Error refreshing block:', error);
      toast({
        variant: 'destructive',
        description: 'Failed to refresh block.',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleEdit = () => {
    onUpdate(block.id, editPrompt);
    setIsEditOpen(false);
  };

  const handleDelete = () => {
    if (confirm('Are you sure you want to delete this block?')) {
      onDelete(block.id);
    }
  };

  const renderBlockContent = () => {
    if (isLoading) {
      return (
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin">
            <RefreshCw className="h-6 w-6" />
          </div>
          <span className="ml-2">Loading...</span>
        </div>
      );
    }

    if (block.status === 'error') {
      return (
        <div className="flex flex-col items-center justify-center h-32 text-muted-foreground">
          <AlertTriangle className="h-8 w-8 text-destructive mb-2" />
          <p className="text-sm">Block encountered an error</p>
          <Button
            variant="outline"
            size="sm"
            onClick={() => onHeal(block.id)}
            className="mt-2"
          >
            Try Auto-Heal
          </Button>
        </div>
      );
    }

    if (!blockData) {
      return (
        <div className="flex items-center justify-center h-32 text-muted-foreground">
          <p className="text-sm">No data available</p>
        </div>
      );
    }

    // For now, show the raw data as JSON
    // In a real implementation, we'd dynamically render the AI-generated React component
    return (
      <div className="space-y-4">
        <div className="text-sm text-muted-foreground">
          Data loaded {blockData.cached ? '(cached)' : '(fresh)'}
        </div>
        <pre className="text-xs bg-muted p-2 rounded overflow-auto max-h-32">
          {JSON.stringify(blockData.data, null, 2)}
        </pre>
      </div>
    );
  };

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="drag-handle cursor-move p-1 hover:bg-muted rounded">
              <Move className="h-4 w-4" />
            </div>
            <CardTitle className="text-lg">{block.title}</CardTitle>
          </div>
          
          <div className="flex items-center space-x-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleRefresh}
              disabled={isLoading}
            >
              <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            </Button>
            
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm">
                  <MoreVertical className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => setIsEditOpen(true)}>
                  <Edit className="h-4 w-4 mr-2" />
                  Edit
                </DropdownMenuItem>
                {block.status === 'error' && (
                  <DropdownMenuItem onClick={() => onHeal(block.id)}>
                    <AlertTriangle className="h-4 w-4 mr-2" />
                    Auto-Heal
                  </DropdownMenuItem>
                )}
                <DropdownMenuSeparator />
                <DropdownMenuItem 
                  onClick={handleDelete}
                  className="text-destructive"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
        
        <div className="text-xs text-muted-foreground">
          {block.user_prompt.substring(0, 100)}
          {block.user_prompt.length > 100 && '...'}
        </div>
      </CardHeader>

      <CardContent className="flex-1 pt-0">
        {renderBlockContent()}
      </CardContent>

      {/* Edit Dialog */}
      <Dialog open={isEditOpen} onOpenChange={setIsEditOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Block</DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4">
            <div>
              <Label htmlFor="prompt">Describe your changes</Label>
              <Input
                id="prompt"
                value={editPrompt}
                onChange={(e) => setEditPrompt(e.target.value)}
                placeholder="Tell me what you want to change about this block..."
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleEdit} disabled={!editPrompt.trim()}>
              Update Block
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Card>
  );
}