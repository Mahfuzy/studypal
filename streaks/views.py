from datetime import date
from django.core.cache import cache
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import StudyStreak, Achievement, XPSystem, Badge, Leaderboard
from .serializers import (
    StudyStreakSerializer, AchievementSerializer, XPSystemSerializer,
    BadgeSerializer, LeaderboardSerializer
)
from study_assistant.ai_service import TaeAI  

# Initialize AI assistant for generating insights
ai_assistant = TaeAI()

# ---------------------- API Views ----------------------

## 📌 Study Streak Views
class StudyStreakListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating study streaks.
    
    Provides functionality to:
    - List all study streaks for the authenticated user
    - Create a new study streak with AI-powered insights
    
    Authentication:
        Requires user to be authenticated.
    """
    permission_classes = [IsAuthenticated]
    queryset = StudyStreak.objects.all()
    serializer_class = StudyStreakSerializer

    # @swagger_auto_schema(
    #     operation_description="List all study streaks for the authenticated user",
    #     responses={
    #         200: openapi.Response(
    #             description="List of study streaks",
    #             schema=StudyStreakSerializer(many=True)
    #         ),
    #         401: "Unauthorized"
    #     }
    # )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    # @swagger_auto_schema(
    #     operation_description="Create a new study streak",
    #     request_body=StudyStreakSerializer,
    #     responses={
    #         201: openapi.Response(
    #             description="Study streak created successfully",
    #             schema=StudyStreakSerializer
    #         ),
    #         400: "Bad Request",
    #         401: "Unauthorized"
    #     }
    # )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        streak = serializer.save()
        insights = ai_assistant.process_text(
            f"Analyze study streak:\nCurrent Streak: {streak.current_streak}\nLongest Streak: {streak.longest_streak}"
        )
        streak.ai_insights = insights
        streak.save()

class StudyStreakDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, and deleting study streaks.
    
    Provides functionality to:
    - Retrieve a specific study streak
    - Update an existing study streak
    - Delete a study streak
    
    Authentication:
        Requires user to be authenticated.
    """
    permission_classes = [IsAuthenticated]
    queryset = StudyStreak.objects.all()
    serializer_class = StudyStreakSerializer

    # @swagger_auto_schema(
    #     operation_description="Retrieve a specific study streak",
    #     responses={
    #         200: openapi.Response(
    #             description="Study streak details",
    #             schema=StudyStreakSerializer
    #         ),
    #         401: "Unauthorized",
    #         404: "Not Found"
    #     }
    # )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    # @swagger_auto_schema(
    #     operation_description="Update an existing study streak",
    #     request_body=StudyStreakSerializer,
    #     responses={
    #         200: openapi.Response(
    #             description="Study streak updated successfully",
    #             schema=StudyStreakSerializer
    #         ),
    #         400: "Bad Request",
    #         401: "Unauthorized",
    #         404: "Not Found"
    #     }
    # )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    # @swagger_auto_schema(
    #     operation_description="Delete a study streak",
    #     responses={
    #         204: "No Content",
    #         401: "Unauthorized",
    #         404: "Not Found"
    #     }
    # )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def perform_update(self, serializer):
        streak = serializer.save()
        insights = ai_assistant.process_text(
            f"Analyze study streak:\nCurrent Streak: {streak.current_streak}\nLongest Streak: {streak.longest_streak}"
        )
        streak.ai_insights = insights
        streak.save()

## 📌 Achievement Views
class AchievementListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating achievements.
    
    Provides functionality to:
    - List all achievements for the authenticated user
    - Create a new achievement with AI-powered insights
    
    Authentication:
        Requires user to be authenticated.
    """
    permission_classes = [IsAuthenticated]
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer

    # @swagger_auto_schema(
    #     operation_description="List all achievements for the authenticated user",
    #     responses={
    #         200: openapi.Response(
    #             description="List of achievements",
    #             schema=AchievementSerializer(many=True)
    #         ),
    #         401: "Unauthorized"
    #     }
    # )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    # @swagger_auto_schema(
    #     operation_description="Create a new achievement",
    #     request_body=AchievementSerializer,
    #     responses={
    #         201: openapi.Response(
    #             description="Achievement created successfully",
    #             schema=AchievementSerializer
    #         ),
    #         400: "Bad Request",
    #         401: "Unauthorized"
    #     }
    # )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        achievement = serializer.save()
        insights = ai_assistant.process_text(
            f"Analyze achievement:\nTitle: {achievement.title}\nDescription: {achievement.description}"
        )
        achievement.ai_insights = insights
        achievement.save()

class AchievementDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, and deleting achievements.
    
    Provides functionality to:
    - Retrieve a specific achievement
    - Update an existing achievement
    - Delete an achievement
    
    Authentication:
        Requires user to be authenticated.
    """
    permission_classes = [IsAuthenticated]
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer

    # @swagger_auto_schema(
    #     operation_description="Retrieve a specific achievement",
    #     responses={
    #         200: openapi.Response(
    #             description="Achievement details",
    #             schema=AchievementSerializer
    #         ),
    #         401: "Unauthorized",
    #         404: "Not Found"
    #     }
    # )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    # @swagger_auto_schema(
    #     operation_description="Update an existing achievement",
    #     request_body=AchievementSerializer,
    #     responses={
    #         200: openapi.Response(
    #             description="Achievement updated successfully",
    #             schema=AchievementSerializer
    #         ),
    #         400: "Bad Request",
    #         401: "Unauthorized",
    #         404: "Not Found"
    #     }
    # )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    # @swagger_auto_schema(
    #     operation_description="Delete an achievement",
    #     responses={
    #         204: "No Content",
    #         401: "Unauthorized",
    #         404: "Not Found"
    #     }
    # )
    @swagger_auto_schema(
        operation_description="Retrieve a specific achievement",
        responses={
            200: openapi.Response(
                description="Achievement details",
                schema=AchievementSerializer
            ),
            401: "Unauthorized",
            404: "Not Found"
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update an existing achievement",
        request_body=AchievementSerializer,
        responses={
            200: openapi.Response(
                description="Achievement updated successfully",
                schema=AchievementSerializer
            ),
            400: "Bad Request",
            401: "Unauthorized",
            404: "Not Found"
        }
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete an achievement",
        responses={
            204: "No Content",
            401: "Unauthorized",
            404: "Not Found"
        }
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def perform_update(self, serializer):
        achievement = serializer.save()
        insights = ai_assistant.process_text(
            f"Analyze achievement:\nTitle: {achievement.title}\nDescription: {achievement.description}"
        )
        achievement.ai_insights = insights
        achievement.save()

## 📌 XP System Views
class XPSystemListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating XP systems.
    
    Provides functionality to:
    - List all XP systems for the authenticated user
    - Create a new XP system with AI-powered insights
    
    Authentication:
        Requires user to be authenticated.
    """
    permission_classes = [IsAuthenticated]
    queryset = XPSystem.objects.all()
    serializer_class = XPSystemSerializer

    # @swagger_auto_schema(
    #     operation_description="List all XP systems for the authenticated user",
    #     responses={
    #         200: openapi.Response(
    #             description="List of XP systems",
    #             schema=XPSystemSerializer(many=True)
    #         ),
    #         401: "Unauthorized"
    #     }
    # )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    # @swagger_auto_schema(
    #     operation_description="Create a new XP system",
    #     request_body=XPSystemSerializer,
    #     responses={
    #         201: openapi.Response(
    #             description="XP system created successfully",
    #             schema=XPSystemSerializer
    #         ),
    #         400: "Bad Request",
    #         401: "Unauthorized"
    #     }
    # )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        xp_system = serializer.save()
        insights = ai_assistant.process_text(
            f"Analyze XP system:\nCurrent XP: {xp_system.current_xp}\nLevel: {xp_system.level}"
        )
        xp_system.ai_insights = insights
        xp_system.save()

class XPSystemDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, and deleting XP systems.
    
    Provides functionality to:
    - Retrieve a specific XP system
    - Update an existing XP system
    - Delete an XP system
    
    Authentication:
        Requires user to be authenticated.
    """
    permission_classes = [IsAuthenticated]
    queryset = XPSystem.objects.all()
    serializer_class = XPSystemSerializer

    # @swagger_auto_schema(
    #     operation_description="Retrieve a specific XP system",
    #     responses={
    #         200: openapi.Response(
    #             description="XP system details",
    #             schema=XPSystemSerializer
    #         ),
    #         401: "Unauthorized",
    #         404: "Not Found"
    #     }
    # )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    # @swagger_auto_schema(
    #     operation_description="Update an existing XP system",
    #     request_body=XPSystemSerializer,
    #     responses={
    #         200: openapi.Response(
    #             description="XP system updated successfully",
    #             schema=XPSystemSerializer
    #         ),
    #         400: "Bad Request",
    #         401: "Unauthorized",
    #         404: "Not Found"
    #     }
    # )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    # @swagger_auto_schema(
    #     operation_description="Delete an XP system",
    #     responses={
    #         204: "No Content",
    #         401: "Unauthorized",
    #         404: "Not Found"
    #     }
    # )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def perform_update(self, serializer):
        xp_system = serializer.save()
        insights = ai_assistant.process_text(
            f"Analyze XP system:\nCurrent XP: {xp_system.current_xp}\nLevel: {xp_system.level}"
        )
        xp_system.ai_insights = insights
        xp_system.save()

## 📌 Leaderboard Views
class LeaderboardListView(generics.ListAPIView):
    """
    API endpoint for listing leaderboard entries with AI insights.
    
    Provides functionality to:
    - List all leaderboard entries
    - Include AI-generated insights about user performance
    
    Authentication:
        Requires user to be authenticated.
    """
    permission_classes = [IsAuthenticated]
    queryset = Leaderboard.objects.all()
    serializer_class = LeaderboardSerializer

    # @swagger_auto_schema(
    #     operation_description="List all leaderboard entries with AI insights",
    #     responses={
    #         200: openapi.Response(
    #             description="Leaderboard entries with AI insights",
    #             schema=openapi.Schema(
    #                 type=openapi.TYPE_OBJECT,
    #                 properties={
    #                     'leaderboard': LeaderboardSerializer(many=True),
    #                     'ai_insights': openapi.Schema(type=openapi.TYPE_STRING),
    #                 }
    #             )
    #         ),
    #         401: "Unauthorized"
    #     }
    # )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        # Get AI insights
        insights = ai_assistant.process_text(
            "Analyze leaderboard trends and provide insights on user performance"
        )
        
        return Response({
            'leaderboard': serializer.data,
            'ai_insights': insights
        })

class LeaderboardDetailView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving a specific leaderboard entry with AI insights.
    
    Provides functionality to:
    - Retrieve a specific leaderboard entry
    - Include AI-generated insights about the user's performance
    
    Authentication:
        Requires user to be authenticated.
    """
    permission_classes = [IsAuthenticated]
    queryset = Leaderboard.objects.all()
    serializer_class = LeaderboardSerializer

    # @swagger_auto_schema(
    #     operation_description="Retrieve a specific leaderboard entry with AI insights",
    #     responses={
    #         200: openapi.Response(
    #             description="Leaderboard entry with AI insights",
    #             schema=openapi.Schema(
    #                 type=openapi.TYPE_OBJECT,
    #                 properties={
    #                     'leaderboard': LeaderboardSerializer,
    #                     'ai_insights': openapi.Schema(type=openapi.TYPE_STRING),
    #                 }
    #             )
    #         ),
    #         401: "Unauthorized",
    #         404: "Not Found"
    #     }
    # )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Get AI insights
        insights = ai_assistant.process_text(
            "Analyze leaderboard trends and provide insights on user performance"
        )
        
        return Response({
            'leaderboard': serializer.data,
            'ai_insights': insights
        })

## 📌 Badge Views
class BadgeListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating badges.
    
    Provides functionality to:
    - List all badges for the authenticated user
    - Create a new badge
    
    Authentication:
        Requires user to be authenticated.
    """
    permission_classes = [IsAuthenticated]
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer

    # @swagger_auto_schema(
    #     operation_description="List all badges for the authenticated user",
    #     responses={
    #         200: openapi.Response(
    #             description="List of badges",
    #             schema=BadgeSerializer(many=True)
    #         ),
    #         401: "Unauthorized"
    #     }
    # )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    # @swagger_auto_schema(
    #     operation_description="Create a new badge",
    #     request_body=BadgeSerializer,
    #     responses={
    #         201: openapi.Response(
    #             description="Badge created successfully",
    #             schema=BadgeSerializer
    #         ),
    #         400: "Bad Request",
    #         401: "Unauthorized"
    #     }
    # )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class BadgeDetailView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving badge details.
    
    Provides functionality to:
    - Retrieve a specific badge's details
    
    Authentication:
        Requires user to be authenticated.
    """
    permission_classes = [IsAuthenticated]
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer

    # @swagger_auto_schema(
    #     operation_description="Retrieve a specific badge's details",
    #     responses={
    #         200: openapi.Response(
    #             description="Badge details",
    #             schema=BadgeSerializer
    #         ),
    #         401: "Unauthorized",
    #         404: "Not Found"
    #     }
    # )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

## 📌 XP & Streak Updates
class UpdateStreakView(APIView):
    """
    API endpoint for updating a user's study streak.
    
    Provides functionality to:
    - Increment the current streak
    - Update the longest streak if applicable
    - Generate AI insights about the streak
    
    Authentication:
        Requires user to be authenticated.
        
    Parameters:
        user_id (int): The ID of the user whose streak should be updated.
    """
    permission_classes = [IsAuthenticated]

    # @swagger_auto_schema(
    #     operation_description="Update user's study streak and generate AI insights",
    #     responses={
    #         200: openapi.Response(
    #             description="Streak updated successfully",
    #             schema=StudyStreakSerializer
    #         ),
    #         401: "Unauthorized",
    #         404: "Not Found"
    #     }
    # )
    def post(self, request, user_id):
        try:
            streak = StudyStreak.objects.get(user_id=user_id)
            streak.current_streak += 1
            streak.longest_streak = max(streak.longest_streak, streak.current_streak)
            
            # Generate AI insights
            insights = ai_assistant.process_text(
                f"Analyze study streak:\nCurrent Streak: {streak.current_streak}\nLongest Streak: {streak.longest_streak}"
            )
            streak.ai_insights = insights
            streak.save()
            
            serializer = StudyStreakSerializer(streak)
            return Response(serializer.data)
        except StudyStreak.DoesNotExist:
            return Response({"error": "Streak not found"}, status=status.HTTP_404_NOT_FOUND)

class AddXPView(APIView):
    """
    API endpoint for adding XP to a user's XP system.
    
    Provides functionality to:
    - Add XP to the user's current XP
    - Update the user's level based on XP thresholds
    - Unlock new badges based on level achievements
    - Generate AI insights about the XP system
    
    Authentication:
        Requires user to be authenticated.
        
    Parameters:
        user_id (int): The ID of the user whose XP should be updated.
        
    Request Body:
        amount (int): The amount of XP to add to the user's current XP.
    """
    permission_classes = [IsAuthenticated]

    # @swagger_auto_schema(
    #     operation_description="Add XP to user's XP system and unlock badges if applicable",
    #     request_body=openapi.Schema(
    #         type=openapi.TYPE_OBJECT,
    #         properties={
    #             'amount': openapi.Schema(type=openapi.TYPE_INTEGER),
    #         }
    #     ),
    #     responses={
    #         200: openapi.Response(
    #             description="XP added successfully",
    #             schema=openapi.Schema(
    #                 type=openapi.TYPE_OBJECT,
    #                 properties={
    #                     'xp_system': XPSystemSerializer,
    #                     'new_badges': BadgeSerializer(many=True),
    #                 }
    #             )
    #         ),
    #         400: "Bad Request",
    #         401: "Unauthorized",
    #         404: "Not Found"
    #     }
    # )
    def post(self, request, user_id):
        try:
            xp_system = XPSystem.objects.get(user_id=user_id)
            amount = request.data.get('amount', 0)
            
            # Add XP and update level
            xp_system.current_xp += amount
            xp_system.level = xp_system.current_xp // 1000  # Level up every 1000 XP
            
            # Generate AI insights
            insights = ai_assistant.process_text(
                f"Analyze XP system:\nCurrent XP: {xp_system.current_xp}\nLevel: {xp_system.level}"
            )
            xp_system.ai_insights = insights
            xp_system.save()
            
            # Check for new badges
            new_badges = []
            if xp_system.level >= 5 and not Badge.objects.filter(user_id=user_id, title="XP Master").exists():
                new_badges.append(Badge.objects.create(
                    user_id=user_id,
                    title="XP Master",
                    description="Reached level 5"
                ))
            
            serializer = XPSystemSerializer(xp_system)
            badge_serializer = BadgeSerializer(new_badges, many=True)
            
            return Response({
                'xp_system': serializer.data,
                'new_badges': badge_serializer.data
            })
        except XPSystem.DoesNotExist:
            return Response({"error": "XP system not found"}, status=status.HTTP_404_NOT_FOUND)
