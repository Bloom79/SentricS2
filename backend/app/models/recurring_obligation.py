"""
Recurring Obligation Model
Tracks annual and recurring compliance obligations for plants
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import BaseModel


class RecurringObligation(BaseModel):
    """Recurring compliance obligation model"""
    __tablename__ = "recurring_obligations"
    
    # Entity relationships
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=True)
    cer_id = Column(Integer, ForeignKey("cer_configuration.id"), nullable=True)
    
    # Obligation details
    obligation_type = Column(String(100), nullable=False)  # 'fuel_mix', 'consumption_declaration', etc.
    entity = Column(String(50), nullable=False)  # 'GSE', 'ADM', 'DSO', 'Terna', 'Comune'
    recurrence_pattern = Column(String(20), nullable=False)  # 'annual', 'quarterly', 'monthly'
    
    # Deadline configuration
    base_deadline = Column(JSON, nullable=False)  # {day: 31, month: 3} or {day: 16, month: 12}
    next_due_date = Column(DateTime, nullable=False)
    last_completed_date = Column(DateTime, nullable=True)
    
    # Workflow automation
    auto_create_workflow = Column(Boolean, default=True)
    workflow_template_id = Column(Integer, nullable=True)
    
    # Notifications
    notification_days = Column(JSON, default=list)  # [90, 60, 30, 7] - days before deadline to notify
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Metadata
    obligation_data = Column(JSON, default=dict)  # Additional obligation-specific data
    notes = Column(Text)
    
    # Relationships
    plant = relationship("Plant", back_populates="recurring_obligations")
    # CER relationship - CER model may not have back_populates defined
    # Using lazy loading to avoid circular imports
    cer = relationship("CER", foreign_keys="[RecurringObligation.cer_id]", lazy="select")
    
    def __repr__(self):
        return f"<RecurringObligation {self.obligation_type} - {self.entity}>"
    
    @property
    def is_overdue(self) -> bool:
        """Check if obligation is overdue"""
        if not self.is_active:
            return False
        return datetime.utcnow() > self.next_due_date
    
    @property
    def days_until_due(self) -> int:
        """Get days until next due date"""
        if not self.is_active:
            return 0
        delta = self.next_due_date - datetime.utcnow()
        return delta.days

