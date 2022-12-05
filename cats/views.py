from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.throttling import AnonRateThrottle, ScopedRateThrottle
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import Achievement, Cat, User

from .serializers import AchievementSerializer, CatSerializer, UserSerializer

from .permissions import OwnerOrReadOnly, ReadOnly

from .throttling import WorkingHoursRateThrottle

from .pagination import CatsPagination


class CatViewSet(viewsets.ModelViewSet):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer
    # Устанавливаем разрешение
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    permission_classes = (OwnerOrReadOnly,)
    # throttle_classes = (AnonRateThrottle,)  # Подключили класс AnonRateThrottle
    # Если кастомный тротлинг-класс вернёт True - запросы будут обработаны
    # Если он вернёт False - все запросы будут отклонены
    throttle_classes = (WorkingHoursRateThrottle, ScopedRateThrottle)
    # Для любых пользователей установим кастомный лимит 1 запрос в минуту
    throttle_scope = 'low_request' # вместо throttle_classes
    # pagination_class = PageNumberPagination
    # pagination_class = LimitOffsetPagination
    # Вот он наш собственный класс пагинации с page_size=20
    # pagination_class = CatsPagination

    # Указываем фильтрующий бэкенд DjangoFilterBackend
    # Из библиотеки django-filter
    # Второй бэкэнд в кортеже - это поиск
    filter_backends = (
        DjangoFilterBackend, # фильтры
        filters.SearchFilter, # поиск по полям
        filters.OrderingFilter # сортировка
    )
    # Временно отключим пагинацию на уровне вьюсета,
    # так будет удобнее настраивать фильтрацию
    pagination_class = None
    # Фильтровать будем по полям color и birth_year модели Cat
    filterset_fields = ('color', 'birth_year')
    search_fields = ('name',)
    # search_fields = ('achievements__name', 'owner__username') # поиск по полям связанных моделей
    # Определим, что значение параметра search должно быть началом искомой строки
    # search_fields = ('^name',)
    ordering_fields = ('name', 'birth_year')
    ordering = ('birth_year',)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user) 

    # def get_permissions(self):
    #     # Если в GET-запросе требуется получить информацию об объекте
    #     if self.action == 'retrieve':
    #         # Вернем обновленный перечень используемых пермишенов
    #         return (ReadOnly(),)
    #     # Для остальных ситуаций оставим текущий перечень пермишенов без изменений
    #     return super().get_permissions()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class AchievementViewSet(viewsets.ModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer