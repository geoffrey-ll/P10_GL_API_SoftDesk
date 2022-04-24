from rest_framework.exceptions import NotAcceptable, NotAuthenticated, \
    NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet, ViewSet


from projects.models import Comment, Contributor, Issue, Project
from projects.serializers import ContributorListSerializer, \
    CommentListSerializer, IssueListSerializer, ProjectListSerializer


# Create your views here.
MESSAGE_NOT_AUTHENTICATED = "Cette API nécessite d'être authentifié."
MESSAGE_NOT_FOUND = "Projet inexistant."
MESSAGE_PERMISSION_DENIED = "Accès refusé."


def check_authenticated(self):
    if self.request.user.is_authenticated is False:
        raise NotAuthenticated(detail=MESSAGE_NOT_AUTHENTICATED)

    project = check_project_exists(self.kwargs)
    try:
        project.contributors.get(user=self.request.user)
        return project
    except:
        raise PermissionDenied(detail=MESSAGE_PERMISSION_DENIED)


def check_project_exists(kwargs):
    if "pk" in kwargs:
    # print(f"\nkwargs:\n{kwargs}\n")
        project_pk = kwargs["pk"]
        print(f"\npk:\n{project_pk}\n")
    # elif kwargs["project_pk"] is True:
    #     project_pk = kwargs["project_pk"]
    try:
        project = Project.objects.get(id=project_pk)
        return project
    except:
        raise NotFound(detail=MESSAGE_NOT_FOUND)




class ContributorViewSet(ModelViewSet):
    serializer_class = ContributorListSerializer

    def get_queryset(self):
        # project = check_authenticated(self)
        project = self.kwargs["project_pk"]
        return Contributor.objects.filter(project=project)

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            project = Project.objects.get(id=self.kwargs["project_pk"])
            try:
                return serializer.save(project=project)
            except:
                raise NotAcceptable(
                    "Un seul superviseur par project. "
                    "Ce project a déjà un superviseur."
                )


class CommentViewSet(ModelViewSet):
    serializer_class = CommentListSerializer

    def get_queryset(self):
        # check_authenticated(self)
        return Comment.objects.filter(issue=self.kwargs["issue_pk"])

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            issue = Issue.objects.get(id=self.kwargs["issue_pk"])
            return serializer.save(issue=issue, author_user=self.request.user)


class IssueViewSet(ModelViewSet):
    serializer_class = IssueListSerializer

    def get_queryset(self):
        # project = check_authenticated(self)
        project = self.kwargs["project_pk"]
        return Issue.objects.filter(project=project)

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            project = Project.objects.get(id=self.kwargs["project_pk"])


            contributors_user = [c.user for c in project.contributors.all()]
            assigned_user = serializer.validated_data['assignee_user']

            if assigned_user not in contributors_user:
                raise NotAcceptable(
                    "L'utilisateur n'est pas contributeur à ce project."
                )
            return serializer.save(
                project=project, author_user=self.request.user
            )



class ProjectViewSet(ModelViewSet):
    serializer_class = ProjectListSerializer

    def get_queryset(self):
        # check_authenticated(self)
        contributors_user = Contributor.objects.filter(user=self.request.user)
        projects_user = [c.project.id for c in contributors_user]
        return Project.objects.filter(id__in=projects_user)

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            try:
                instance = serializer.save(author_user=self.request.user)
                Contributor.objects.create(
                    user=self.request.user, project=instance, role='m'
                )
                return
            except:
                raise NotAcceptable(
                    "Plusieurs projects de même type ne peuvent pas partagés "
                    "le même nom."
                )
