import asyncio
import schedule
import time
import threading
from datetime import datetime
from app.services.sync_service import sync_service


class SchedulerService:
    def __init__(self):
        self.is_running = False
        self.thread = None
    
    def start_scheduler(self):
        """Bắt đầu scheduler"""
        if self.is_running:
            print("⚠️ Scheduler is already running")
            return
        
        print("🚀 Starting scheduler service...")
        self.is_running = True
        
        # Schedule sync job mỗi giờ
        schedule.every().hour.do(self.run_sync_job)
        
        # Chạy scheduler trong thread riêng
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        
        print("✅ Scheduler started successfully")
        print("📅 Sync job scheduled to run every hour")
    
    def stop_scheduler(self):
        """Dừng scheduler"""
        if not self.is_running:
            print("⚠️ Scheduler is not running")
            return
        
        print("🛑 Stopping scheduler service...")
        self.is_running = False
        schedule.clear()
        
        if self.thread:
            self.thread.join(timeout=5)
        
        print("✅ Scheduler stopped successfully")
    
    def _run_scheduler(self):
        """Chạy scheduler loop"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check mỗi phút
    
    def run_sync_job(self):
        """Chạy sync job"""
        try:
            print(f"🔄 Scheduled sync job started at {datetime.now()}")
            result = sync_service.sync_all_novels()
            
            if result['success']:
                print(f"✅ Scheduled sync job completed successfully")
                print(f"   📚 Novels processed: {result['novels_processed']}")
                print(f"   ⏱️ Duration: {result['duration']:.2f}s")
            else:
                print(f"❌ Scheduled sync job failed")
                print(f"   📚 Novels processed: {result['novels_processed']}")
                print(f"   ❌ Errors: {result['novels_error']}")
                
        except Exception as e:
            print(f"❌ Error in scheduled sync job: {e}")
    
    def get_scheduler_status(self):
        """Lấy trạng thái scheduler"""
        return {
            "is_running": self.is_running,
            "next_job": schedule.next_run().isoformat() if schedule.jobs else None,
            "jobs_count": len(schedule.jobs)
        }


# Global scheduler instance
scheduler_service = SchedulerService() 