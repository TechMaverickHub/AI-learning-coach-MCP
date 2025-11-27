from django.apps import AppConfig


class BackendConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend'
    
    def ready(self):
        # Start scheduler when Django app is ready
        # Note: Tasks run synchronously in background threads
        try:
            from .scheduler import start_scheduler
            start_scheduler()
        except Exception as e:
            # Log error but don't crash if scheduler fails
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to start scheduler: {e}")

