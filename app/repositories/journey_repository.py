class JourneyRepository:
    def __init__(self, db):
        self.db = db

    async def get_user_profile(self, user_id):
        return await self.db.profiles.find_one(
            {"user_id": user_id}
        )

    async def get_learning_progress(self, user_id):
        return await self.db.progress.find_one(
            {"user_id": user_id}
        )

    async def get_job_application(self, user_id):
        return await self.db.job_applications.find_one(
            {"user_id": user_id}
        )

    async def get_career_plan(self, user_id):
        return await self.db.career_plans.find_one(
            {"user_id": user_id}
        )