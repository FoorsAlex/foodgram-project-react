from rest_framework import viewsets, mixins


class RetrieveListCreateViewSet(mixins.RetrieveModelMixin,
                                mixins.ListModelMixin,
                                mixins.CreateModelMixin,
                                viewsets.GenericViewSet):
    pass
