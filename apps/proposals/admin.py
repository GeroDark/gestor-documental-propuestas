from django.contrib import admin

from .models import Comment, Proposal, ProposalStatusHistory


class ProposalStatusHistoryInline(admin.TabularInline):
    model = ProposalStatusHistory
    extra = 0
    readonly_fields = ("previous_status", "new_status", "comment", "changed_by", "changed_at")
    can_delete = False


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ("user", "content", "created_at")
    can_delete = False


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "client",
        "responsible",
        "estimated_amount",
        "due_date",
        "status",
        "created_by",
        "created_at",
    )
    list_filter = ("status", "due_date", "created_at")
    search_fields = ("title", "client__business_name", "description")
    ordering = ("-created_at",)
    inlines = [ProposalStatusHistoryInline, CommentInline]


@admin.register(ProposalStatusHistory)
class ProposalStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("proposal", "previous_status", "new_status", "changed_by", "changed_at")
    list_filter = ("new_status", "changed_at")
    search_fields = ("proposal__title", "comment", "changed_by__username")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("proposal", "user", "created_at")
    search_fields = ("proposal__title", "content", "user__username")
    list_filter = ("created_at",)