from django.db import models

from django.shortcuts import render, get_object_or_404, redirect
from .models import Ticket, Notification
from .forms import TicketForm
from django.contrib.auth.decorators import login_required
from .forms_profile import ProfileForm
from django.contrib import messages

# Profile view for editing user info
@login_required
def profile(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('tickets:profile')
    else:
        form = ProfileForm(instance=user)
    unread_count = user.notifications.filter(is_read=False).count()
    return render(request, 'tickets/profile.html', {'form': form, 'unread_count': unread_count, 'user': user})

# Notifications page view
@login_required
def notifications(request):
    unread_count = request.user.notifications.filter(is_read=False).count()
    return render(request, 'tickets/notifications.html', {'unread_count': unread_count})

# ----------------------
# Ticket Views
# ----------------------

@login_required
def ticket_list(request):
    user = request.user
    if hasattr(user, 'role') and user.role == 'helper':
        # Order by priority (high > medium > low) and then by created_at descending
        priority_order = models.Case(
            models.When(priority='high', then=0),
            models.When(priority='medium', then=1),
            models.When(priority='low', then=2),
            output_field=models.IntegerField(),
        )
        tickets = Ticket.objects.filter(status__in=['open', 'in_progress']).order_by(priority_order, '-created_at')
    else:
        tickets = Ticket.objects.filter(created_by=user).exclude(status='closed').order_by('-created_at')
    unread_count = user.notifications.filter(is_read=False).count()
    return render(request, 'tickets/ticket_list.html', {'tickets': tickets, 'unread_count': unread_count})

@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    # Handle rating submission
    if request.method == 'POST' and ticket.status == 'closed' and request.user == ticket.created_by:
        rating = request.POST.get('rating')
        if rating and rating.isdigit() and 1 <= int(rating) <= 5:
            ticket.rating = int(rating)
            ticket.save()
            # Notify the helper (if any) that the ticket was rated
            if ticket.justification and ticket.rating:
                helpers = Notification.objects.filter(user__role='helper')
                for helper in helpers:
                    Notification.objects.create(
                        user=helper.user,
                        message=f"Ticket '{ticket.title}' was rated {ticket.rating}/5 by {request.user.username}."
                    )
            return redirect('tickets:ticket_detail', pk=ticket.pk)
    unread_count = request.user.notifications.filter(is_read=False).count()
    return render(request, 'tickets/ticket_detail.html', {
        'ticket': ticket,
        'unread_count': unread_count
    })

@login_required
def ticket_create(request):
    # Only staff can create tickets
    if not hasattr(request.user, 'role') or request.user.role != 'staff':
        return redirect('tickets:ticket_list')
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.save()
            return redirect('tickets:ticket_list')
    else:
        form = TicketForm()
    unread_count = request.user.notifications.filter(is_read=False).count()
    return render(request, 'tickets/ticket_form.html', {'form': form, 'unread_count': unread_count})

@login_required
def ticket_update(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    # Only staff who created the ticket can edit
    if request.user.role == 'staff' and ticket.created_by == request.user:
        if request.method == 'POST':
            form = TicketForm(request.POST, instance=ticket)
            if form.is_valid():
                form.save()
                return redirect('tickets:ticket_detail', pk=ticket.pk)
        else:
            form = TicketForm(instance=ticket)
        unread_count = request.user.notifications.filter(is_read=False).count()
        return render(request, 'tickets/ticket_form.html', {'form': form, 'unread_count': unread_count})
    # Only helpers can close/justify
    elif request.user.role == 'helper':
        if request.method == 'POST':
            justification = request.POST.get('justification')
            ticket.justification = justification
            ticket.status = 'closed'
            ticket.save()
            # Notify the ticket creator
            Notification.objects.create(
                user=ticket.created_by,
                message=f"Your ticket '{ticket.title}' was closed by helper {request.user.username}. Justification: {justification}"
            )
            # Notify the helper (themselves)
            Notification.objects.create(
                user=request.user,
                message=f"You closed ticket '{ticket.title}' for {ticket.created_by.username}. Justification: {justification}"
            )
            return redirect('tickets:ticket_detail', pk=ticket.pk)
        unread_count = request.user.notifications.filter(is_read=False).count()
        return render(request, 'tickets/ticket_justify.html', {'ticket': ticket, 'unread_count': unread_count})
    else:
        return redirect('tickets:ticket_list')

@login_required
def ticket_delete(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    # Only staff who created the ticket can delete
    if request.user.role == 'staff' and ticket.created_by == request.user:
        if request.method == 'POST':
            ticket.delete()
            return redirect('tickets:ticket_list')
        unread_count = request.user.notifications.filter(is_read=False).count()
        return render(request, 'tickets/ticket_confirm_delete.html', {'ticket': ticket, 'unread_count': unread_count})
    else:
        return redirect('tickets:ticket_list')


# ----------------------
# Pages & Auth Views
# ----------------------
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm

def home(request):
    """Login page"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('tickets:ticket_list')
    else:
        form = AuthenticationForm()
    unread_count = request.user.notifications.filter(is_read=False).count() if request.user.is_authenticated else 0
    return render(request, 'home.html', {'form': form, 'unread_count': unread_count})

def signup(request):
    """User registration"""
    error_message = ''
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                return redirect('tickets:ticket_list')
            except Exception as e:
                if 'UNIQUE constraint failed' in str(e):
                    error_message = 'Username already exists. Please choose another.'
                else:
                    error_message = 'Sign up failed: ' + str(e)
        else:
            error_message = 'Invalid sign up – try again.'
    else:
        form = CustomUserCreationForm()
    unread_count = request.user.notifications.filter(is_read=False).count() if request.user.is_authenticated else 0
    return render(request, 'signup.html', {'form': form, 'error_message': error_message, 'unread_count': unread_count})

def about(request):
    unread_count = request.user.notifications.filter(is_read=False).count() if request.user.is_authenticated else 0
    return render(request, 'about.html', {'unread_count': unread_count})
