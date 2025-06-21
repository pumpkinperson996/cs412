# project/api_views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.db.models import Avg
from .models import Restroom, Stall, Review, Order, Product, User
from .serializers import (
    RestroomSerializer,
    StallSerializer,
    ReviewSerializer,
    OrderSerializer,
    ProductSerializer,
    UserSerializer,
    UserRegistrationSerializer,
)

# ==================== 认证相关视图 ====================

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """用户注册"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """用户登录"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': '请提供用户名和密码'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        })
    return Response(
        {'error': '用户名或密码错误'}, 
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """用户登出"""
    try:
        request.user.auth_token.delete()
        return Response({'message': '成功退出'})
    except:
        return Response({'error': '退出失败'}, status=status.HTTP_400_BAD_REQUEST)


# ==================== 洗手间相关视图 ====================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def restroom_list(request):
    """获取洗手间列表或创建新洗手间"""
    if request.method == 'GET':
        # 获取所有洗手间，包含平均评分
        restrooms = Restroom.objects.annotate(
            avg_rating=Avg('review__rating')
        ).order_by('-created_at')
        serializer = RestroomSerializer(restrooms, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # 创建新洗手间
        serializer = RestroomSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def restroom_detail(request, restroom_id):
    """获取、更新或删除单个洗手间"""
    try:
        restroom = Restroom.objects.get(id=restroom_id)
    except Restroom.DoesNotExist:
        return Response(
            {'error': '洗手间不存在'}, 
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':
        # 获取洗手间详情，包含所有stalls和最近的评论
        restroom_data = RestroomSerializer(restroom).data
        
        # 添加stalls信息
        stalls = Stall.objects.filter(restroom=restroom)
        restroom_data['stalls'] = StallSerializer(stalls, many=True).data
        
        # 添加最近5条评论
        recent_reviews = Review.objects.filter(
            restroom=restroom
        ).order_by('-created_at')[:5]
        restroom_data['recent_reviews'] = ReviewSerializer(recent_reviews, many=True).data
        
        return Response(restroom_data)
    
    elif request.method == 'PUT':
        # 只有创建者可以修改
        if restroom.created_by != request.user:
            return Response(
                {'error': '您没有权限修改此洗手间'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = RestroomSerializer(restroom, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        # 只有创建者可以删除
        if restroom.created_by != request.user:
            return Response(
                {'error': '您没有权限删除此洗手间'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        restroom.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ==================== Stall相关视图 ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_stall_status(request, stall_id):
    """更新stall占用状态"""
    try:
        stall = Stall.objects.get(id=stall_id)
    except Stall.DoesNotExist:
        return Response(
            {'error': 'Stall不存在'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    is_occupied = request.data.get('is_occupied')
    if is_occupied is None:
        return Response(
            {'error': '请提供is_occupied状态'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    stall.is_occupied = is_occupied
    stall.save()
    return Response(StallSerializer(stall).data)


# ==================== 评论相关视图 ====================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def reviews(request):
    """获取所有评论或创建新评论"""
    if request.method == 'GET':
        # 可以通过查询参数过滤特定洗手间的评论
        restroom_id = request.query_params.get('restroom_id')
        if restroom_id:
            reviews = Review.objects.filter(restroom_id=restroom_id)
        else:
            reviews = Review.objects.all()
        
        reviews = reviews.order_by('-created_at')
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            # 检查评分范围
            rating = serializer.validated_data.get('rating')
            if rating < 1 or rating > 5:
                return Response(
                    {'error': '评分必须在1-5之间'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer.save(author=request.user)
            
            # 更新洗手间的平均评分
            restroom = serializer.validated_data['restroom']
            avg_rating = Review.objects.filter(
                restroom=restroom
            ).aggregate(Avg('rating'))['rating__avg']
            restroom.avg_rating = avg_rating or 0
            restroom.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==================== 产品相关视图 ====================

@api_view(['GET'])
@permission_classes([AllowAny])  # 产品列表可以公开访问
def product_list(request):
    """获取所有产品"""
    products = Product.objects.filter(stock_qty__gt=0)  # 只显示有库存的产品
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


# ==================== 订单相关视图 ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_order(request):
    """提交订单"""
    serializer = OrderSerializer(data=request.data)
    if serializer.is_valid():
        # 验证库存
        items = serializer.validated_data.get('items', {})
        for product_id, quantity in items.items():
            try:
                product = Product.objects.get(id=product_id)
                if product.stock_qty < quantity:
                    return Response(
                        {'error': f'{product.name}库存不足'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except Product.DoesNotExist:
                return Response(
                    {'error': f'产品ID {product_id} 不存在'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # 创建订单
        order = serializer.save(buyer=request.user, status='pending')
        
        # 更新库存
        for product_id, quantity in items.items():
            product = Product.objects.get(id=product_id)
            product.stock_qty -= quantity
            product.save()
        
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_orders(request):
    """获取当前用户的所有订单"""
    orders = Order.objects.filter(buyer=request.user).order_by('-created_at')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


# ==================== 用户相关视图 ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """获取当前用户信息"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """更新用户信息"""
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)