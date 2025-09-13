import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';

interface AddBlockDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (userPrompt: string, title?: string) => void;
}

export function AddBlockDialog({ open, onOpenChange, onSubmit }: AddBlockDialogProps) {
  const [userPrompt, setUserPrompt] = useState('');
  const [title, setTitle] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!userPrompt.trim()) return;
    
    setIsSubmitting(true);
    try {
      await onSubmit(userPrompt, title || undefined);
      
      // Reset form
      setUserPrompt('');
      setTitle('');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      onOpenChange(false);
      // Reset form on close
      setUserPrompt('');
      setTitle('');
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Add New Block</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <div>
            <Label htmlFor="title">Title (optional)</Label>
            <Input
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g., Weather Widget, Stock Prices..."
              disabled={isSubmitting}
            />
          </div>

          <div>
            <Label htmlFor="prompt">
              Describe what you want this block to show
            </Label>
            <Textarea
              id="prompt"
              value={userPrompt}
              onChange={(e) => setUserPrompt(e.target.value)}
              placeholder="e.g., Show me the current weather in San Francisco with a 5-day forecast..."
              className="min-h-[100px]"
              disabled={isSubmitting}
            />
          </div>

          <div className="text-sm text-muted-foreground space-y-2">
            <p className="font-medium">Examples:</p>
            <ul className="list-disc pl-4 space-y-1">
              <li>"Show me Bitcoin price with a chart"</li>
              <li>"Display top 5 Hacker News stories"</li>
              <li>"Weather forecast for New York"</li>
              <li>"List latest GitHub commits for my project"</li>
            </ul>
          </div>
        </div>

        <DialogFooter>
          <Button 
            variant="outline" 
            onClick={handleClose}
            disabled={isSubmitting}
          >
            Cancel
          </Button>
          <Button 
            onClick={handleSubmit} 
            disabled={!userPrompt.trim() || isSubmitting}
          >
            {isSubmitting ? 'Creating...' : 'Create Block'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}