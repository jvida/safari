from PIL import Image
from PIL import ImageOps
from io import BytesIO
from django.core.files.base import ContentFile
from catalog.models import Park, Customer, Trip
from catalog.forms import TripForm, SingleTripForm
import json
from django.core.serializers import serialize
from django.core.mail import send_mail
from safari.settings import EMAIL_HOST_USER, EMAIL_SUBJECT_PREFIX, EMAIL_ADDRESS_FOR_NEW_ORDERS


def expedition_helper(exp_type):
    if exp_type == "safari":
        num_parks = Park.objects.filter(safari=True).count()
        trip_form = TripForm
        single_trip = False
    else:
        num_parks = 1
        trip_form = SingleTripForm
        single_trip = True
    return num_parks, trip_form, single_trip


def create_email_msg(expedition, order_type):
    msg = ""
    customer = Customer.objects.get(id=expedition['customer'])
    msg += f'Order type: {order_type} \n\n' \
           f'Customer: {customer.user.username} \n' \
           f'Name: {customer.user.first_name}, {customer.user.last_name}\n\n' \
           f'Date: {expedition["date_from"]} - {expedition["date_to"]}\n' \
           f'Number of people: {expedition["number_of_people"]}\n\n'

    for trip_id in expedition["trips"]:
        trip = Trip.objects.get(id=trip_id)
        msg += f'{trip.park}\n' \
               f'Accommodation: {trip.accommodation}\n' \
               f'Days: {trip.days}\n\n'
    if expedition["message_for_us"]:
        msg += f'Message for us:\n{expedition["message_for_us"]}\n'

    return msg


def send_order(expedition, order_type):
    serialized_obj = json.loads(serialize('json', [expedition]))[0]
    email_content = create_email_msg(serialized_obj['fields'], order_type)
    send_mail(EMAIL_SUBJECT_PREFIX + " " + order_type, email_content, EMAIL_HOST_USER,
              [EMAIL_ADDRESS_FOR_NEW_ORDERS])


def resize_image(image: Image, length: int, content_file: bool):
    """
    Resizes an image to a square. Can make an image bigger to make it fit or smaller if it doesn't fit. It also crops
    part of the image.

    :param image: Image to resize.
    :param length: Width and height of the output image.
    :param content_file: Whether to return Image or ContentFile
    :return: Return the resized image either as Image or ContentFile.
    """

    image = ImageOps.exif_transpose(image)

    """
    Resizing strategy : 
     1) We resize the smallest side to the desired dimension (e.g. 1080)
     2) We crop the other side so as to make it fit with the same length as the smallest side (e.g. 1080)
    """
    if image.size[0] < image.size[1]:
        # The image is in portrait mode. Height is bigger than width.

        # This makes the width fit the LENGTH in pixels while conserving the ration.
        resized_image = image.resize((length, int(image.size[1] * (length / image.size[0]))))

        # Amount of pixel to lose in total on the height of the image.
        required_loss = (resized_image.size[1] - length)

        # Crop the height of the image so as to keep the center part.
        resized_image = resized_image.crop(
            box=(0, required_loss / 2, length, resized_image.size[1] - required_loss / 2))

    else:
        # This image is in landscape mode or already squared. The width is bigger than the heihgt.

        # This makes the height fit the LENGTH in pixels while conserving the ration.
        resized_image = image.resize((int(image.size[0] * (length / image.size[1])), length))

        # Amount of pixel to lose in total on the width of the image.
        required_loss = resized_image.size[0] - length

        # Crop the width of the image so as to keep 1080 pixels of the center part.
        resized_image = resized_image.crop(
            box=(required_loss / 2, 0, resized_image.size[0] - required_loss / 2, length))

    # We now have a length*length pixels image.
    if content_file:
        square_io = BytesIO()
        resized_image.save(square_io, format='JPEG')
        return ContentFile(square_io.getvalue())
    else:
        return resized_image
