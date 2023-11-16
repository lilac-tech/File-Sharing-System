from django.http import request
from django.shortcuts import render, redirect, get_object_or_404
from pathlib import Path
from user.models import User
from docs.models import Document, Comment
from announcements.models import Announcement
from django.contrib import messages
from django.contrib import auth
from tqdm import tqdm
from django.contrib.auth.decorators import login_required
from PyPDF2 import PdfReader, PdfWriter
from pdf2image.pdf2image import convert_from_path
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
BASE_DI = Path(__file__).resolve().parent.parent
video_formats = ["mp4", "mkv"]


@login_required(login_url='login')
def home_view(request):
    """
    Renders the home.html template for an authenticated user.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered home.html template.
    """
    return render(request, "home.html")


@login_required(login_url='login')
def search_view(request):
    """
    This function is the view for the search functionality. It is decorated with the `@login_required` decorator, which ensures that only authenticated users can access this view. 

    Parameters:
    - `request`: The HTTP request object.

    Returns:
    - If the request method is POST and the `search` key is present in the POST data, the function filters the `Document` objects based on the `doc_name` field and the authenticated user's division. It then renders the `search.html` template with the filtered documents and the `video_formats` context variable.
    - If the request method is not POST, the function filters the `Document` objects based on an empty `doc_name` field. It then renders the `search.html` template with the filtered documents and the `video_formats` context variable.
    - If the request method is neither POST nor GET, the function renders the `search.html` template.

    Note:
    - The `login_url` argument in the `@login_required` decorator specifies the URL to redirect to if the user is not authenticated.
    """
    if request.method == 'POST':
        if 'search' in request.POST:
            search_item = request.POST['search']
            documents = Document.objects.all().filter(
                doc_name__icontains=search_item, division__exact=request.user.division)
            return render(request, "search.html", {'documents': documents, 'video_formats': video_formats})
    else:
        documents = Document.objects.all().filter(division__exact=request.user.division)
        return render(request, "search.html", {'documents': documents, 'video_formats': video_formats})
    return render(request, "search.html")


def login_view(request):
    """
    Logs in a user based on the provided request.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.
    """
    if request.method == 'POST':
        id = request.POST['Id']
        password1 = request.POST['password']
        user = auth.authenticate(username=id, password=password1)
        if user is not None:
            auth.login(request, user)
            return redirect('/home/')
        else:
            messages.info(request, "Invalid credentials")
    return render(request, "login.html")


def logout_view(request):
    """
    View function for logging out a user.

    Parameters:
        request (HttpRequest): The HTTP request object.
    
    Returns:
        HttpResponse: The HTTP response object.
    """
    auth.logout(request)
    return redirect('/home/')


def signup_view(request):
    """
    View function for signing up a user.
    
    Parameters:
        request (HttpRequest): The HTTP request object.
        
    Returns:
        HttpResponse: The HTTP response object.
    """
    divisions = ['1', '2', '3']
    
    if request.method == 'POST':
        id = request.POST['id']
        password1 = request.POST['password']
        password2 = request.POST['confirm-password']
        name = request.POST['name']
        division = request.POST['division']
        
        if password1 == password2:
            if User.objects.filter(name=name).exists():
                messages.info(request, "Username already exists")
            elif User.objects.filter(id=id).exists():
                messages.info(request, "id already exists")
            elif division not in divisions:
                messages.info(request, "Enter a valid division")
            else:
                try:
                    user = User.object.create_user(id=id, name=name, password=password1, division=division)
                    user.save()
                    return redirect('/login/')
                except ValueError as e:
                    messages.info(request, str(e))
        else:
            messages.info(request, "passwords do not match")

    return render(request, "sign_up.html", {"divisions": divisions})


@login_required(login_url='login')
def file_upload_view(request):
    """
    This function handles the file upload view.
    
    Parameters:
    - `request`: The HTTP request object.
    
    Returns:
    - If the user is a staff or an admin and the request method is POST, the function performs the following steps:
        - Iterates over each file in the `document` list obtained from the request's `FILES` attribute.
        - Checks if a document with the same `doc_name` already exists in the database. If it does, a message is displayed and the loop continues with the next file.
        - If the file is a PDF, it converts the first page of the PDF to an image and saves it as a JPEG file.
        - If the file is a JPEG, JPG, or PNG file, it sets `img_file` to the file itself.
        - Creates a new `Document` object in the database with the following attributes:
            - `doc_name`: The name of the document extracted from the uploaded file's name.
            - `size`: The size of the file in megabytes.
            - `document`: The uploaded file itself.
            - `file_type`: The file extension extracted from the uploaded file's name.
            - `thumbnail`: The image file saved earlier (if applicable).
            - `division`: The division associated with the user who uploaded the file.
            - `uploaded_by`: The user who uploaded the file.
        - Saves the `Document` object in the database.
        - If any exception occurs during the above steps, an error message is displayed.
    
    - If the user is not a staff or an admin, a message is displayed indicating that they do not have the necessary privileges.
    
    - Finally, the function renders the `in.html` template.
    
    Note: 
    - The `tqdm` library is used to display an upload progress bar (in the terminal).
    - The `login_url` argument in the `@login_required` decorator specifies the URL to redirect to if the user is not authenticated.
    """
    if request.user.is_staff or request.user.is_admin:
        if request.method == 'POST':
            for file in tqdm(request.FILES.getlist('document'), desc="Upload progress", unit="files", leave=True):
                doc_name = "".join(file.name.split('.')[:-1])
                if Document.objects.filter(doc_name=doc_name).exists():
                    messages.info(request, f"File {file.name} already exists")
                    continue
                if file.name.lower().endswith('.pdf'):
                    pdf_reader = PdfReader(file)
                    pdf_writer = PdfWriter()
                    pdf_writer.add_page(pdf_reader.pages[0])
                    with open("temp.pdf", "wb") as f:
                        pdf_writer.write(f)
                    images = convert_from_path(
                        "temp.pdf",
                        poppler_path="poppler-22.04.0/Library/bin"
                    )
                    thumbnail_io = BytesIO()
                    images[0].save(thumbnail_io, format='JPEG')
                    thumbnail = InMemoryUploadedFile(
                        file=thumbnail_io,
                        field_name=None,
                        name=doc_name + ".jpeg",
                        content_type='image/jpeg',
                        size=images[0].tell(),
                        charset=None
                    )
                elif file.name.lower().endswith((".jpg", ".png", ".jpeg")):
                    thumbnail = file
                else:
                    thumbnail = None
                try:
                    doc = Document.objects.create(
                        doc_name=doc_name,
                        size=file.size / (1024 * 1024),
                        document=file,
                        file_type=file.name.split('.')[-1],
                        thumbnail=thumbnail,
                        division=request.user.division,
                        uploaded_by=request.user,
                    )
                    doc.save()
                except Exception as e:
                    messages.info(request, str(e))
    else:
        messages.info(request, "You are not a staff or an administrator")
    return render(request, "in.html")


@login_required(login_url='login')
def file_view(request, doc_id):
    """
    Renders the view for a specific file.

    Args:
        request (HttpRequest): The HTTP request object.
        doc_id (str): The ID of the document to be rendered.

    Returns:
        HttpResponse: The rendered file view.

    Raises:
        Http404: If the document is not found.

    Side Effects:
        - Increments the 'times_viewed' field of the document.
        - Creates a new comment if a POST request is made.

    Notes:
        - The `login_url` argument in the `@login_required` decorator specifies the URL to redirect to if the user is not authenticated.
    """
    document = Document.objects.filter(doc_id=doc_id)[0]

    document.times_viewed += 1
    document.save()
    
    comments = document.comments.filter(active=True) # type: ignore
    # Comment posted
    if request.method == 'POST':
        print(request.POST['body'], request.user.name, request.user.id, document.doc_name)
        comment = Comment.objects.create(body=request.POST['body'], name=request.user.name,
                                         user_id=request.user.id, document=document)
        comment.save()
    return render(request, "file_view.html", {
        'document': document,
        'comments': comments,
        'video_formats': video_formats,
    })


@login_required(login_url='login')
def download_file(request):
    """
    Downloads a file and updates the download count.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.
    
    Notes:
        - The `login_url` argument in the `@login_required` decorator specifies the URL to redirect to if the user is not authenticated.
    """
    if request.method == "POST":
        if form.is_valid():
            doc_name = request.POST.get("id")
            doc = get_object_or_404(Document, doc_name=doc_name)
            doc.times_downloaded += 1
            doc.save()
            return render(request, "download.html", {'doc': doc})


def about_us_view(request):
    """
    Renders the "about us" page.

    Args:
        request: The HTTP request.

    Returns:
        The rendered "about us" HTML page.
    """
    return render(request, "about_us.html")


def announcement_view(request):
    """
    Render the announcement view for the given request.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered announcement view.

    Raises:
        None
    """
    division = request.user.division
    announcements = Announcement.objects.filter(division=division)
    return render(request, "announcement.html", {"announcements": announcements})
