from django.contrib import admin

# Register your models here.
# Added Language to the import list
from .models import Author, Genre, Book, BookInstance, Language

# admin.site.register(Author)
# Define the admin class
# Part 4 Challenge Yourself #2
class BookInline(admin.TabularInline):
    model = Book
    extra = 0

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')

    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]

    inlines = [BookInline]

# Register the admin class with the associated model
admin.site.register(Author, AuthorAdmin)

# admin.site.register(Book)
# admin.site.register(BookInstance)
# Register the Admin classes for Book using the decorator
class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
    extra = 0

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')

    inlines = [BooksInstanceInline]
	
# Register the Admin classes for BookInstance using the decorator
@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
		# Part 4 Challenge Yourself #1
		list_display = ('book', 'status', 'borrower', 'due_back', 'id')	
		list_filter = ('status', 'due_back')

		fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back', 'borrower')
        }),
    )

admin.site.register(Genre)
# Added Language to be registered
admin.site.register(Language)