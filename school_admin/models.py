# school_admin/models.py
import uuid
from django.db import models
from django.conf import settings
from tenants.models import TenantAwareModel

class ActivityLog(TenantAwareModel):
    """Tracks administrative actions across the school."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action_type = models.CharField(max_length=50)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.action_type}] {self.description[:30]}"


class Notification(TenantAwareModel):
    """System alerts and mapping requests for the dashboard."""
    TYPE_CHOICES = (
        ('alert', 'Alert'),
        ('system', 'System'),
        ('mapping', 'Mapping'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='system')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({'Read' if self.is_read else 'Unread'})"


class SchoolSettings(TenantAwareModel):
    """Stores configurable settings for each school."""
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    grading_scale = models.CharField(max_length=20, default='4.0 GPA')
    attendance_tracking_enabled = models.BooleanField(default=True)
    default_academic_year = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        verbose_name_plural = "School Settings"

    def __str__(self):
        return f"Settings for {self.school.name}"


class Grievance(TenantAwareModel):
    """
    Student/Parent grievance tracking system.
    """
    class PriorityChoices(models.TextChoices):
        LOW = 'Low', 'Low'
        MEDIUM = 'Medium', 'Medium'
        HIGH = 'High', 'High'
        URGENT = 'Urgent', 'Urgent'

    class StatusChoices(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        IN_PROGRESS = 'In-Progress', 'In-Progress'
        RESOLVED = 'Resolved', 'Resolved'
        CLOSED = 'Closed', 'Closed'
        REJECTED = 'Rejected', 'Rejected'

    class SourceChoices(models.TextChoices):
        STUDENT = 'Student', 'Student'
        PARENT = 'Parent', 'Parent'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Who submitted the grievance
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='submitted_grievances'
    )
    source_type = models.CharField(max_length=20, choices=SourceChoices.choices)
    
    # Optional: Link to specific student (if parent submits for a child)
    student = models.ForeignKey(
        'profiles.StudentProfile', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='grievances'
    )
    
    # Grievance details
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100, blank=True, null=True)
    priority = models.CharField(max_length=20, choices=PriorityChoices.choices, default=PriorityChoices.MEDIUM)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    
    # Admin/Staff resolution details
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_grievances'
    )
    admin_remarks = models.TextField(blank=True, null=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['submitted_by', 'status']),
        ]

    def __str__(self):
        return f"{self.title[:50]} - {self.status} ({self.submitted_by.email})"