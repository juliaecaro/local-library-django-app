from django.shortcuts import render

# Create your views here.
from .models import Book, Author, BookInstance, Genre

def index(request):
    # View function for home page of site.

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

		# Part 5 Challenge Yourself #2
		# Generate counts for genres that contain a particular word (case insensitive)		
    # Fiction Genre
    young_genre = Book.objects.filter(genre__name__icontains='young adult').count()
    short_genre = Book.objects.filter(genre__name__icontains='short stories').count()
    historical_genre = Book.objects.filter(genre__name__icontains='historical fiction').count()
    science_genre = Book.objects.filter(genre__name__icontains='science fiction').count()
    dystopia_genre = Book.objects.filter(genre__name__icontains='dystopia').count()
    mystery_genre = Book.objects.filter(genre__name__icontains='mystery').count()
    realistic_genre = Book.objects.filter(genre__name__icontains='realistic fiction').count()
    # Counting the Fiction Genre total
    fiction_genre = young_genre + short_genre + historical_genre + science_genre + dystopia_genre + mystery_genre + realistic_genre

    # Nonfiction Genre
    memoir_genre = Book.objects.filter(genre__name__icontains='memoir').count()
    biography_genre = Book.objects.filter(genre__name__icontains='biography').count()
    # Counting the Nonfiction Genre total
    nonfiction_genre = memoir_genre + biography_genre
	
		# Generate counts for books that contain a particular word (case insensitive)
    # Fiction Genre Available Books
    young_genre_available = BookInstance.objects.filter(book__genre__name__icontains='young adult', status__exact='a').count()
    short_genre_available = BookInstance.objects.filter(book__genre__name__icontains='short stories', status__exact='a').count()
    historical_genre_available = BookInstance.objects.filter(book__genre__name__icontains='historical fiction', status__exact='a').count()
    science_genre_available = BookInstance.objects.filter(book__genre__name__icontains='science fiction', status__exact='a').count()
    dystopia_genre_available = BookInstance.objects.filter(book__genre__name__icontains='dystopia', status__exact='a').count()
    mystery_genre_available = BookInstance.objects.filter(book__genre__name__icontains='mystery', status__exact='a').count()
    realistic_genre_available = BookInstance.objects.filter(book__genre__name__icontains='realistic fiction', status__exact='a').count()
    # Counting the Fiction Genre available total   
    fiction_genre_available = young_genre_available + short_genre_available + historical_genre_available + science_genre_available + dystopia_genre_available + mystery_genre_available + realistic_genre_available

    # Nonfiction Genre Available Books
    memoir_genre_available = BookInstance.objects.filter(book__genre__name__icontains='memoir', status__exact='a').count()
    biography_genre_available = BookInstance.objects.filter(book__genre__name__icontains='biography', status__exact='a').count()
    # Counting the Nonfiction Genre available total
    nonfiction_genre_available = memoir_genre_available + biography_genre_available

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'fiction_genre': fiction_genre,
        'fiction_genre_available': fiction_genre_available,
				'nonfiction_genre': nonfiction_genre,
        'nonfiction_genre_available': nonfiction_genre_available,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

from django.views import generic

class BookDetailView(generic.DetailView):
    model = Book

class BookListView(generic.ListView):
    model = Book
    # paginate_by changed from 10 to 6
    paginate_by = 6

# Part 6 Challenge Yourself
class AuthorDetailView(generic.DetailView):
    model = Author

class AuthorListView(generic.ListView):
    model = Author
    # paginate_by changed from 10 to 6
    paginate_by = 6

from django.contrib.auth.mixins import LoginRequiredMixin

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    # Generic class-based view listing books on loan to current user.
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    # paginate_by changed from 10 to 6
    paginate_by = 6

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact='o')
            .order_by('due_back')
        )

# Part 8 Challenge Yourself
from django.contrib.auth.mixins import PermissionRequiredMixin

class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    # Generic class-based view listing books on loan to every user. Only visible to users with can_mark_returned permission.
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    # paginate_by changed from 10 to 6
    paginate_by = 6
   
    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')

import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from catalog.forms import RenewBookForm

@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    # View function for renewing a specific BookInstance by librarian.
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from catalog.models import Author

class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    permission_required = 'catalog.can_mark_returned'
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '01/01/2000'}

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    permission_required = 'catalog.can_mark_returned'
    fields = '__all__' # Not recommended (potential security issue if more fields added)

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    permission_required = 'catalog.can_mark_returned'
    success_url = reverse_lazy('authors')

# Part 9 Challenge Yourself
from catalog.models import Book

class BookCreate(CreateView):
    model = Book
    permission_required = 'catalog.can_mark_returned'
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']

class BookUpdate(UpdateView):
    model = Book
    permission_required = 'catalog.can_mark_returned'
    fields = '__all__' # Not recommended (potential security issue if more fields added)

class BookDelete(DeleteView):
    model = Book
    permission_required = 'catalog.can_mark_returned'
    success_url = reverse_lazy('books')