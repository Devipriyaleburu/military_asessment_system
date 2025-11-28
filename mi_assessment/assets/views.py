from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from .models import *
from .serializers import *
from django.db.models import Sum, F
from rest_framework.authtoken.models import Token
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db.models import Q
from datetime import datetime
from .decorators import role_required, base_restricted
from .forms import PurchaseForm, TransferForm, AssignmentForm

# Utility to create audit log
def log_action(user, action, details=""):
    Log.objects.create(user=user if user and user.is_authenticated else None, action=action, details=details)

def home(request):
    return render(request, 'assets/index.html')

@login_required
def dashboard(request):
    base_filter = request.GET.get('base')
    asset_filter = request.GET.get('asset')
    date_filter = request.GET.get('date')

    assets = Asset.objects.all()
    if base_filter:
        assets = assets.filter(base_id=base_filter)
    if asset_filter:
        assets = assets.filter(id=asset_filter)

    # Calculate metrics
    total_opening = sum(asset.opening_balance for asset in assets)
    total_closing = sum(asset.closing_balance for asset in assets)
    total_net_movement = sum(asset.net_movement for asset in assets)
    total_assigned = sum(asset.assigned for asset in assets)
    total_expended = sum(asset.expended for asset in assets)

    bases = Base.objects.all()
    asset_types = Asset.objects.values('type').distinct()

    context = {
        'total_opening': total_opening,
        'total_closing': total_closing,
        'total_net_movement': total_net_movement,
        'total_assigned': total_assigned,
        'total_expended': total_expended,
        'bases': bases,
        'asset_types': asset_types,
        'selected_base': base_filter,
        'selected_asset': asset_filter,
    }
    return render(request, 'assets/dashboard.html', context)

@login_required
def purchases(request):
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            purchase = form.save()
            purchase.asset.update_closing_balance()
            messages.success(request, 'Purchase recorded successfully.')
            return redirect('purchases')
        else:
            messages.error(request, 'Error: Please correct the form errors.')
    else:
        form = PurchaseForm()

    base_filter = request.GET.get('base')
    asset_filter = request.GET.get('asset')
    date_filter = request.GET.get('date')

    purchases = Purchase.objects.all()
    if base_filter:
        purchases = purchases.filter(asset__base_id=base_filter)
    if asset_filter:
        purchases = purchases.filter(asset_id=asset_filter)
    if date_filter:
        purchases = purchases.filter(date=date_filter)

    bases = Base.objects.all()
    assets = Asset.objects.all()
    types = Asset.objects.values_list('type', flat=True).distinct()

    context = {
        'purchases': purchases,
        'bases': bases,
        'assets': assets,
        'types': types,
        'selected_base': base_filter,
        'selected_asset': asset_filter,
        'selected_date': date_filter,
        'form': form,
    }
    return render(request, 'assets/purchases.html', context)

@login_required
def transfers(request):
    if request.method == 'POST':
        form = TransferForm(request.POST)
        if form.is_valid():
            transfer = form.save()
            # Update balances
            from_asset = Asset.objects.filter(base=transfer.from_base, name=transfer.asset.name, type=transfer.asset.type).first()
            to_asset = Asset.objects.filter(base=transfer.to_base, name=transfer.asset.name, type=transfer.asset.type).first()
            if from_asset:
                from_asset.update_closing_balance()
            if to_asset:
                to_asset.update_closing_balance()
            messages.success(request, 'Transfer recorded successfully.')
            return redirect('transfers')
        else:
            messages.error(request, 'Error: Please correct the form errors.')
    else:
        form = TransferForm()

    base_filter = request.GET.get('base')
    asset_filter = request.GET.get('asset')
    date_filter = request.GET.get('date')

    transfers = Transfer.objects.all()
    if base_filter:
        transfers = transfers.filter(Q(from_base_id=base_filter) | Q(to_base_id=base_filter))
    if asset_filter:
        transfers = transfers.filter(asset_id=asset_filter)
    if date_filter:
        transfers = transfers.filter(timestamp__date=date_filter)

    bases = Base.objects.all()
    assets = Asset.objects.all()

    context = {
        'transfers': transfers,
        'bases': bases,
        'assets': assets,
        'selected_base': base_filter,
        'selected_asset': asset_filter,
        'selected_date': date_filter,
        'form': form,
    }
    return render(request, 'assets/transfers.html', context)

@login_required
def assignments(request):
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save()
            assignment.asset.update_closing_balance()
            messages.success(request, 'Assignment recorded successfully.')
            return redirect('assignments')
        else:
            messages.error(request, 'Error: Please correct the form errors.')
    else:
        form = AssignmentForm()

    base_filter = request.GET.get('base')
    asset_filter = request.GET.get('asset')
    date_filter = request.GET.get('date')

    assignments = Assignment.objects.all()
    if base_filter:
        assignments = assignments.filter(asset__base_id=base_filter)
    if asset_filter:
        assignments = assignments.filter(asset_id=asset_filter)
    if date_filter:
        assignments = assignments.filter(date=date_filter)

    bases = Base.objects.all()
    assets = Asset.objects.all()

    context = {
        'assignments': assignments,
        'bases': bases,
        'assets': assets,
        'selected_base': base_filter,
        'selected_asset': asset_filter,
        'selected_date': date_filter,
        'form': form,
    }
    return render(request, 'assets/assignments.html', context)

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        from django.contrib.auth import authenticate, login
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials.')
    return render(request, 'assets/login.html')

def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('login')

# API Views
class ObtainAuthTokenView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        from django.contrib.auth import authenticate
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if not user:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "role": user.role, "base_id": user.base.id if user.base else None})

class DashboardView(APIView):
    def get(self, request):
        base_filter = getattr(request, "base_filter", None)
        balances_qs = Asset.objects.all()
        purchases_qs = Purchase.objects.all()
        transfers_in_qs = Transfer.objects.all()
        transfers_out_qs = Transfer.objects.all()
        assignments_qs = Assignment.objects.all()

        if base_filter:
            balances_qs = balances_qs.filter(base=base_filter)
            purchases_qs = purchases_qs.filter(asset__base=base_filter)
            transfers_in_qs = transfers_in_qs.filter(to_base=base_filter)
            transfers_out_qs = transfers_out_qs.filter(from_base=base_filter)
            assignments_qs = assignments_qs.filter(asset__base=base_filter)

        purchases_count = purchases_qs.count()
        transfers_in_count = transfers_in_qs.count()
        transfers_out_count = transfers_out_qs.count()
        assignments_count = assignments_qs.count()

        balances = AssetSerializer(balances_qs, many=True).data

        data = {
            "balances": balances,
            "purchases_count": purchases_count,
            "transfers_in_count": transfers_in_count,
            "transfers_out_count": transfers_out_count,
            "assignments_count": assignments_count,
        }
        return Response(data)

class PurchaseListCreate(APIView):
    def get(self, request):
        qs = Purchase.objects.all()
        bf = getattr(request, "base_filter", None)
        if bf:
            qs = qs.filter(asset__base=bf)
        serializer = PurchaseSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        data["created_by"] = request.user.id if request.user.is_authenticated else None
        serializer = PurchaseSerializer(data=data)
        if serializer.is_valid():
            p = serializer.save()
            log_action(request.user, "create_purchase", f"Purchase id={p.id} base={p.asset.base} qty={p.quantity}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TransferListCreate(APIView):
    def get(self, request):
        qs = Transfer.objects.all()
        bf = getattr(request, "base_filter", None)
        if bf:
            qs = qs.filter(Q(from_base=bf) | Q(to_base=bf))
        serializer = TransferSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        data["created_by"] = request.user.id if request.user.is_authenticated else None
        serializer = TransferSerializer(data=data)
        if serializer.is_valid():
            t = serializer.save()
            log_action(request.user, "create_transfer", f"Transfer id={t.id} from={t.from_base} to={t.to_base} qty={t.quantity}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AssignmentListCreate(APIView):
    def get(self, request):
        qs = Assignment.objects.all()
        bf = getattr(request, "base_filter", None)
        if bf:
            qs = qs.filter(asset__base=bf)
        serializer = AssignmentSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        data["created_by"] = request.user.id if request.user.is_authenticated else None
        serializer = AssignmentSerializer(data=data)
        if serializer.is_valid():
            a = serializer.save()
            log_action(request.user, "create_assignment", f"Assignment id={a.id} base={a.asset.base} qty={a.quantity}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BaseList(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        return Response(BaseSerializer(Base.objects.all(), many=True).data)

class AssetList(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        return Response(AssetSerializer(Asset.objects.all(), many=True).data)
