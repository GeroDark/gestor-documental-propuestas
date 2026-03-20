from rest_framework import serializers

from .models import Comment, Proposal, ProposalStatusHistory


class ProposalStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_username = serializers.CharField(source="changed_by.username", read_only=True)

    class Meta:
        model = ProposalStatusHistory
        fields = [
            "id",
            "previous_status",
            "new_status",
            "comment",
            "changed_by",
            "changed_by_username",
            "changed_at",
        ]


class CommentSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "proposal", "user", "user_username", "content", "created_at"]
        read_only_fields = ("proposal", "user", "created_at")


class ProposalSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.business_name", read_only=True)
    responsible_name = serializers.CharField(source="responsible.username", read_only=True)
    created_by_username = serializers.CharField(source="created_by.username", read_only=True)
    status_history = ProposalStatusHistorySerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Proposal
        fields = [
            "id",
            "client",
            "client_name",
            "title",
            "description",
            "responsible",
            "responsible_name",
            "estimated_amount",
            "due_date",
            "status",
            "created_by",
            "created_by_username",
            "created_at",
            "updated_at",
            "status_history",
            "comments",
        ]
        read_only_fields = ("created_by", "created_at", "updated_at")