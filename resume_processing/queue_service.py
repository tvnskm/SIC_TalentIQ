class ResumeQueueService:
    """
    Queue implementation for resume processing.
    Backed by ProcessingQueue database model.
    Demonstrates: Queue ADT — FIFO, enqueue, dequeue, peek.
    """
    
    def enqueue(self, resume_id: int, priority: int = 1):
        from resume_processing.models import ProcessingQueue
        return ProcessingQueue.objects.create(
            resume_id=resume_id,
            status='PENDING',
            priority=priority
        )
    
    def dequeue(self):
        """Remove and return the next item (highest priority, oldest first)."""
        from resume_processing.models import ProcessingQueue
        item = (ProcessingQueue.objects
                .filter(status='PENDING')
                .order_by('-priority', 'created_at')
                .first())
        if item:
            item.status = 'PROCESSING'
            item.save()
        return item
    
    def peek(self):
        """Return the next item without removing it."""
        from resume_processing.models import ProcessingQueue
        return (ProcessingQueue.objects
                .filter(status='PENDING')
                .order_by('-priority', 'created_at')
                .first())
    
    def complete(self, queue_item_id: int):
        from resume_processing.models import ProcessingQueue
        from django.utils import timezone
        ProcessingQueue.objects.filter(id=queue_item_id).update(
            status='COMPLETED',
            processed_at=timezone.now()
        )
    
    def fail(self, queue_item_id: int):
        from resume_processing.models import ProcessingQueue
        ProcessingQueue.objects.filter(id=queue_item_id).update(status='FAILED')
    
    def queue_size(self) -> int:
        from resume_processing.models import ProcessingQueue
        return ProcessingQueue.objects.filter(status='PENDING').count()
    
    def is_empty(self) -> bool:
        return self.queue_size() == 0
