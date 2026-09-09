from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Expenses ,Income, Category , Budget
from django.db.models import Sum
from django.utils import timezone


@api_view(['GET'])
def hello_api(request):
    return Response({
        "message": "Hello World",
        "status": "success"
    })
@api_view(['POST'])
def register(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if not username:
        return Response({
            "error" : "invalid user"
        },status = 400)
    if not email:
        return Response({
            "error": "Email is required"
        }, status=400)
    if not password:
        return Response({
            "error": "Password is required"
        }, status=400)
    if User.objects.filter(username=username).exists():
        return Response({
            "error": "Username already exists"
        }, status=400)

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )

    return Response({
        "message": "User registered successfully",
        "data": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }, status=201)

@api_view(['GET', 'POST', 'DELETE', 'PUT', 'PATCH'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_expenses(request):

    # =========================
    # GET - Get Expenses
    # =========================
    if request.method == 'GET':

        category = request.query_params.get('category')
        date = request.query_params.get('date')

        expenses = Expenses.objects.filter(
            user=request.user
        )

        if category:
            expenses = expenses.filter(
                category_obj__name=category
            )

        if date:
            expenses = expenses.filter(
                created_at__date=date
            )

        data = []

        for expense in expenses:
            data.append({
                "id": expense.id,
                "amount": expense.amount,
                "category": (
                    expense.category_obj.name
                    if expense.category_obj
                    else None
                ),
                "created_at": expense.created_at
            })

        return Response(data)

    # =========================
    # POST - Add Expense
    # =========================
    elif request.method == 'POST':

        data = request.data

        amount = data.get('amount')
        category_id = data.get('category_id')

        # Amount required
        if amount is None:
            return Response(
                {"error": "Amount is required"},
                status=400
            )

        # Amount must be number
        try:
            amount = int(amount)
        except (ValueError, TypeError):
            return Response(
                {"error": "Amount must be a number"},
                status=400
            )

        # Amount must be positive
        if amount <= 0:
            return Response(
                {"error": "Amount must be greater than 0"},
                status=400
            )

        # Category required
        if category_id is None:
            return Response(
                {"error": "Category ID is required"},
                status=400
            )

        try:
            category = Category.objects.get(
                id=category_id,
                user=request.user
            )

            expense = Expenses.objects.create(
                user=request.user,
                amount=amount,
                category_obj=category
            )

            return Response({
                "message": "Expense created successfully",
                "data": {
                    "id": expense.id,
                    "amount": expense.amount,
                    "category": category.name
                }
            }, status=201)

        except Category.DoesNotExist:
            return Response(
                {"error": "Category not found"},
                status=404
            )

    # =========================
    # DELETE
    # =========================
    elif request.method == 'DELETE':

        expense_id = request.data.get('id')

        if not expense_id:
            return Response(
                {"error": "Expense ID is required"},
                status=400
            )

        try:
            expense = Expenses.objects.get(
                id=expense_id,
                user=request.user
            )

            expense.delete()

            return Response({
                "message": "Expense deleted successfully"
            })

        except Expenses.DoesNotExist:
            return Response(
                {"error": "Expense not found"},
                status=404
            )

    # =========================
    # PUT
    # =========================
    elif request.method == 'PUT':

        expense_id = request.data.get('id')

        if not expense_id:
            return Response(
                {"error": "Expense ID is required"},
                status=400
            )

        if 'amount' not in request.data:
            return Response(
                {"error": "Amount is required"},
                status=400
            )

        if 'category_id' not in request.data:
            return Response(
                {"error": "Category ID is required"},
                status=400
            )

        try:
            amount = int(request.data['amount'])

            if amount <= 0:
                return Response(
                    {"error": "Amount must be greater than 0"},
                    status=400
                )

            expense = Expenses.objects.get(
                id=expense_id,
                user=request.user
            )

            category = Category.objects.get(
                id=request.data['category_id'],
                user=request.user
            )

            expense.amount = amount
            expense.category_obj = category
            expense.save()

            return Response({
                "message": "Expense updated successfully",
                "data": {
                    "id": expense.id,
                    "amount": expense.amount,
                    "category": category.name
                }
            })

        except Expenses.DoesNotExist:
            return Response(
                {"error": "Expense not found"},
                status=404
            )

        except Category.DoesNotExist:
            return Response(
                {"error": "Category not found"},
                status=404
            )

        except (ValueError, TypeError):
            return Response(
                {"error": "Amount must be a number"},
                status=400
            )

    # =========================
    # PATCH
    # =========================
    elif request.method == 'PATCH':

        expense_id = request.data.get('id')

        if not expense_id:
            return Response(
                {"error": "Expense ID is required"},
                status=400
            )

        try:
            expense = Expenses.objects.get(
                id=expense_id,
                user=request.user
            )

            if 'amount' in request.data:

                try:
                    amount = int(request.data['amount'])
                except (ValueError, TypeError):
                    return Response(
                        {"error": "Amount must be a number"},
                        status=400
                    )

                if amount <= 0:
                    return Response(
                        {"error": "Amount must be greater than 0"},
                        status=400
                    )

                expense.amount = amount

            if 'category_id' in request.data:

                try:
                    category = Category.objects.get(
                        id=request.data['category_id'],
                        user=request.user
                    )

                    expense.category_obj = category

                except Category.DoesNotExist:
                    return Response(
                        {"error": "Category not found"},
                        status=404
                    )

            expense.save()

            return Response({
                "message": "Expense partially updated successfully",
                "data": {
                    "id": expense.id,
                    "amount": expense.amount,
                    "category": (
                        expense.category_obj.name
                        if expense.category_obj
                        else None
                    )
                }
            })

        except Expenses.DoesNotExist:
            return Response(
                {"error": "Expense not found"},
                status=404
            )

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def add_income(request):

    data = request.data

    amount = request.data.get('amount')

    if amount is None:
        return Response(
            {"error": "Amount is required"},
            status=400
        )

    try:
        amount = int(amount)
    except (ValueError, TypeError):
        return Response(
            {"error": "Amount must be a number"},
            status=400
        )

    if amount <= 0:
        return Response(
            {"error": "Amount must be greater than 0"},
            status=400
        )

    if 'source' not in data:
        return Response({
            "error": "Source is required"
        }, status=400)

    income = Income.objects.create(
        user=request.user,
        amount=amount,
        source=request.data.get('source')
    )

    return Response({
        "message": "Income added successfully",
        "data": {
            "id": income.id,
            "amount": income.amount,
            "source": income.source
        }
    }, status=201)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_income(request):

    incomes = Income.objects.filter(user=request.user)

    data = []

    for income in incomes:
        data.append({
            "id": income.id,
            "amount": income.amount,
            "source": income.source
        })

    return Response({
        "message": "Income fetched successfully",
        "data": data
    })
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_income(request):

    income_id = request.data.get('id')

    if not income_id:
        return Response({
            "error": "Income ID is required"
        }, status=400)

    try:
        income = Income.objects.get(
            id=income_id,
            user=request.user
        )

        income.delete()

        return Response({
            "message": "Income deleted successfully"
        })

    except Income.DoesNotExist:
        return Response({
            "error": "Income not found"
        }, status=404)

@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_income(request):

    income_id = request.data.get('id')

    if not income_id:
        return Response({
            "error": "Income ID is required"
        }, status=400)

    if 'amount' not in request.data:
        return Response({
            "error": "Amount is required"
        }, status=400)

    if 'source' not in request.data:
        return Response({
            "error": "Source is required"
        }, status=400)

    try:
        income = Income.objects.get(
            id=income_id,
            user=request.user
        )

        income.amount = request.data['amount']
        income.source = request.data['source']

        income.save()

        return Response({
            "message": "Income updated successfully",
            "data": {
                "id": income.id,
                "amount": income.amount,
                "source": income.source
            }
        })

    except Income.DoesNotExist:
        return Response({
            "error": "Income not found"
        }, status=404)

@api_view(['PATCH'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def patch_income(request):

    income_id = request.data.get('id')

    if not income_id:
        return Response({
            "error": "Income ID is required"
        }, status=400)

    try:
        income = Income.objects.get(
            id=income_id,
            user=request.user
        )

        if 'amount' in request.data:
            income.amount = request.data['amount']

        if 'source' in request.data:
            income.source = request.data['source']

        income.save()

        return Response({
            "message": "Income partially updated successfully",
            "data": {
                "id": income.id,
                "amount": income.amount,
                "source": income.source
            }
        })

    except Income.DoesNotExist:
        return Response({
            "error": "Income not found"
        }, status=404)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def add_category(request):

    name = request.data.get('name')

    # 1. Category name check
    if not name:
        return Response(
            {"error": "Category name is required"},
            status=400
        )

    # 2. Duplicate category check
    if Category.objects.filter(
        user=request.user,
        name__iexact=name
    ).exists():
        return Response(
            {"error": "Category already exists"},
            status=400
        )

    # 3. Create category
    category = Category.objects.create(
        user=request.user,
        name=name
    )

    return Response({
        "message": "Category added successfully",
        "data": {
            "id": category.id,
            "name": category.name
        }
    }, status=201)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_categories(request):

    categories = Category.objects.filter(
        user=request.user
    )

    data = []

    for category in categories:
        data.append({
            "id": category.id,
            "name": category.name
        })

    return Response(data)

@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_category(request):

    category_id = request.data.get('id')
    name = request.data.get('name')

    if not category_id:
        return Response({
            "error": "Category ID is required"
        }, status=400)

    if not name:
        return Response({
            "error": "Category name is required"
        }, status=400)

    try:
        category = Category.objects.get(
            id=category_id,
            user=request.user
        )

        category.name = name
        category.save()

        return Response({
            "message": "Category updated successfully",
            "data": {
                "id": category.id,
                "name": category.name
            }
        })

    except Category.DoesNotExist:
        return Response({
            "error": "Category not found"
        }, status=404)


@api_view(['PATCH'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def patch_category(request):

    category_id = request.data.get('id')

    if not category_id:
        return Response({
            "error": "Category ID is required"
        }, status=400)

    try:
        category = Category.objects.get(
            id=category_id,
            user=request.user
        )

        if 'name' in request.data:
            category.name = request.data['name']

        category.save()

        return Response({
            "message": "Category partially updated successfully",
            "data": {
                "id": category.id,
                "name": category.name
            }
        })

    except Category.DoesNotExist:
        return Response({
            "error": "Category not found"
        }, status=404)

@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_category(request):

    category_id = request.data.get('id')

    if not category_id:
        return Response({
            "error": "Category ID is required"
        }, status=400)

    try:
        category = Category.objects.get(
            id=category_id,
            user=request.user
        )

        category.delete()

        return Response({
            "message": "Category deleted successfully"
        })

    except Category.DoesNotExist:
        return Response({
            "error": "Category not found"
        }, status=404)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def monthly_report(request):

    month = request.query_params.get('month')

    if not month:
        return Response({
            "error": "Month is required. Use YYYY-MM format."
        }, status=400)

    try:
        year, month_number = map(int, month.split('-'))

    except ValueError:
        return Response({
            "error": "Invalid month format. Use YYYY-MM."
        }, status=400)

    expenses = Expenses.objects.filter(
        user=request.user,
        created_at__year=year,
        created_at__month=month_number
    )

    income = Income.objects.filter(
        user=request.user,
        created_at__year=year,
        created_at__month=month_number
    )

    total_expense = expenses.aggregate(
        total=Sum('amount')
    )['total'] or 0

    total_income = income.aggregate(
        total=Sum('amount')
    )['total'] or 0

    balance = total_income - total_expense

    return Response({
        "month": month,
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance
    })


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def set_budget(request):

    amount = request.data.get('amount')
    month = request.data.get('month')

    if not amount:
        return Response({
            "error": "Budget amount is required"
        }, status=400)

    if not month:
        return Response({
            "error": "Month is required. Use YYYY-MM format."
        }, status=400)

    budget = Budget.objects.create(
        user=request.user,
        amount=amount,
        month=month
    )

    return Response({
        "message": "Budget set successfully",
        "data": {
            "id": budget.id,
            "amount": budget.amount,
            "month": budget.month
        }
    }, status=201)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_budget(request):

    month = request.query_params.get('month')

    if not month:
        return Response({
            "error": "Month is required. Use YYYY-MM format."
        }, status=400)

    try:
        budget = Budget.objects.get(
            user=request.user,
            month=month
        )
    except Budget.DoesNotExist:
        return Response({
            "error": "Budget not found"
        }, status=404)

    year, month_number = map(int, month.split('-'))

    expenses = Expenses.objects.filter(
        user=request.user,
        created_at__year=year,
        created_at__month=month_number
    )

    total_expense = expenses.aggregate(
        total=Sum('amount')
    )['total'] or 0

    remaining = budget.amount - total_expense

    if remaining >= 0:
        status = "Within Budget"
    else:
        status = "Over Budget"

    return Response({
        "month": month,
        "budget": budget.amount,
        "total_expense": total_expense,
        "remaining": remaining,
        "status": status
    })

@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_budget(request):

    budget_id = request.data.get('id')
    amount = request.data.get('amount')

    if not budget_id:
        return Response({
            "error": "Budget ID is required"
        }, status=400)

    if amount is None:
        return Response(
            {"error": "Budget amount is required"},
            status=400
        )

    try:
        amount = int(amount)
    except (ValueError, TypeError):
        return Response(
            {"error": "Budget amount must be a number"},
            status=400
        )

    if amount <= 0:
        return Response(
            {"error": "Budget amount must be greater than 0"},
            status=400
        )

    try:
        budget = Budget.objects.get(
            id=budget_id,
            user=request.user
        )

        budget.amount = amount
        budget.save()

        return Response({
            "message": "Budget updated successfully",
            "data": {
                "id": budget.id,
                "amount": budget.amount,
                "month": budget.month
            }
        })

    except Budget.DoesNotExist:
        return Response({
            "error": "Budget not found"
        }, status=404)


@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_budget(request):

    budget_id = request.data.get('id')

    if not budget_id:
        return Response({
            "error": "Budget ID is required"
        }, status=400)

    try:
        budget = Budget.objects.get(
            id=budget_id,
            user=request.user
        )

        budget.delete()

        return Response({
            "message": "Budget deleted successfully"
        })

    except Budget.DoesNotExist:
        return Response({
            "error": "Budget not found"
        }, status=404)

import re

@api_view(['PATCH'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def patch_budget(request):

    budget_id = request.data.get('id')

    if not budget_id:
        return Response(
            {"error": "Budget ID is required"},
            status=400
        )

    try:
        budget = Budget.objects.get(
            id=budget_id,
            user=request.user
        )

        # Amount update
        if 'amount' in request.data:

            try:
                amount = int(request.data['amount'])
            except (ValueError, TypeError):
                return Response(
                    {"error": "Budget amount must be a number"},
                    status=400
                )

            if amount <= 0:
                return Response(
                    {"error": "Budget amount must be greater than 0"},
                    status=400
                )

            budget.amount = amount

        # Month update
        if 'month' in request.data:

            month = request.data['month']

            if not re.fullmatch(
                r'\d{4}-(0[1-9]|1[0-2])',
                month
            ):
                return Response(
                    {"error": "Invalid month format. Use YYYY-MM."},
                    status=400
                )

            # Duplicate month check
            if Budget.objects.filter(
                user=request.user,
                month=month
            ).exclude(id=budget.id).exists():

                return Response(
                    {"error": "Budget already exists for this month"},
                    status=400
                )

            budget.month = month

        budget.save()

        return Response({
            "message": "Budget partially updated successfully",
            "data": {
                "id": budget.id,
                "amount": budget.amount,
                "month": budget.month
            }
        })

    except Budget.DoesNotExist:
        return Response(
            {"error": "Budget not found"},
            status=404
        )

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def set_budget(request):

    amount = request.data.get('amount')
    month = request.data.get('month')

    # Amount check
    if amount is None:
        return Response(
            {"error": "Budget amount is required"},
            status=400
        )

    try:
        amount = int(amount)
    except (ValueError, TypeError):
        return Response(
            {"error": "Budget amount must be a number"},
            status=400
        )

    if amount <= 0:
        return Response(
            {"error": "Budget amount must be greater than 0"},
            status=400
        )

    # Month check
    if not month:
        return Response(
            {"error": "Month is required. Use YYYY-MM format."},
            status=400
        )

    if not re.fullmatch(r'\d{4}-(0[1-9]|1[0-2])', month):
        return Response(
            {"error": "Invalid month format. Use YYYY-MM."},
            status=400
        )

    # Duplicate budget check
    if Budget.objects.filter(
        user=request.user,
        month=month
    ).exists():
        return Response(
            {"error": "Budget already exists for this month"},
            status=400
        )

    budget = Budget.objects.create(
        user=request.user,
        amount=amount,
        month=month
    )

    return Response({
        "message": "Budget set successfully",
        "data": {
            "id": budget.id,
            "amount": budget.amount,
            "month": budget.month
        }
    }, status=201)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def dashboard(request):

    month = request.query_params.get('month')

    if not month:
        return Response(
            {"error": "Month is required. Use YYYY-MM format."},
            status=400
        )

    # Month format check
    try:
        year, month_number = map(int, month.split('-'))
    except ValueError:
        return Response(
            {"error": "Invalid month format. Use YYYY-MM."},
            status=400
        )
    if month_number < 1 or month_number > 12:
        return Response(
            {"error": "Invalid month. Month must be between 01 and 12."},
            status=400
        )

    # User's expenses for selected month
    expenses = Expenses.objects.filter(
        user=request.user,
        created_at__year=year,
        created_at__month=month_number
    )

    # User's income for selected month
    incomes = Income.objects.filter(
        user=request.user,
        created_at__year=year,
        created_at__month=month_number
    )

    # Total expense
    total_expense = expenses.aggregate(
        total=Sum('amount')
    )['total'] or 0

    # Total income
    total_income = incomes.aggregate(
        total=Sum('amount')
    )['total'] or 0

    # Balance
    balance = total_income - total_expense

    # Budget
    try:
        budget = Budget.objects.get(
            user=request.user,
            month=month
        )
        budget_amount = budget.amount
        remaining_budget = budget_amount - total_expense
    except Budget.DoesNotExist:
        budget_amount = 0
        remaining_budget = 0

    # Category-wise expense
    category_data = []

    categories = expenses.values(
        'category_obj__name'
    ).annotate(
        total=Sum('amount')
    ).order_by('-total')

    for category in categories:
        category_data.append({
            "category": category['category_obj__name'],
            "amount": category['total']
        })

    return Response({
        "month": month,
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance,
        "budget": budget_amount,
        "remaining_budget": remaining_budget,
        "category_wise_expense": category_data
    })