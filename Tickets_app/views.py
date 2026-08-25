

import hashlib

from django.shortcuts import render, redirect
from pymongo import MongoClient
from bson.objectid import ObjectId
from django.shortcuts import render





client = MongoClient("mongodb+srv://bnivedha400_db_user:xilZAchSySuoql4f@cluster0.dz4he2r.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["Train_Booking"]
col = db["Train"]
booking_col = db ["bookings"]
user_col = db["users"] 

                                                                                                
                                                                                            


def index(request):
    return render(request, "index.html")




def home(request):
    return render(request, "homepage.html")



def train_list(request):
    if request.method == "POST":
        source = request.POST.get("from")
        destination = request.POST.get("to")
        date = request.POST.get("date")
        travel_class = request.POST.get("class")

        trains = list(col.find({
            "source": source,
            "destination": destination
        }))

        for train in trains:
            train["id"] = str(train["_id"])

        return render(request, "results.html", {
            "trains": trains,
            "source": source,
            "destination": destination,
            "date": date,
            "class": travel_class
        })

    return redirect("/")







import hashlib

def register(request):
    if request.method == "POST":
        name = request.POST.get("full_name")
        age = request.POST.get("age")
        email = request.POST.get("email")
        gender = request.POST.get("gender")
        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")

        # check empty
        if not name or not age or not email or not password:
            return render(request, "register.html", {"error": "All fields are required"})

        # password match
        if password != confirm:
            return render(request, "register.html", {"error": "Passwords do not match"})

        # check existing email
        if user_col.find_one({"email": email}):   
            return render(request, "register.html", {"error": "Email already exists"})

        # hash password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # insert into MongoDB
        user_col.insert_one({
            "name": name,
            "age": int(age),
            "gender":gender,
            "email": email,
            "password": hashed_password
        })

        return redirect("/login/")
    

    return render(request, "register.html")








def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        user = user_col.find_one({
            "email": email,
            "password": hashed_password
        })

        if user:
         request.session["email"] = user["email"]
         request.session["user"] = user["name"]

         print("LOGIN SESSION:", dict(request.session))

         return redirect("/")
        

        else:
            return render(request, "login.html", {
                "error": "Invalid credentials"
            })

    return render(request, "login.html")




from django.contrib import messages
def logout(request):
    request.session.flush()
    messages.success(request, "Logged out successfully.")
    return redirect("login")






def pnr_status(request):

    booking = None

    if request.method == "POST":

        pnr = request.POST.get("pnr")

        booking = booking_col.find_one({
            "pnr": int(pnr)
        })

    return render(request, "pnr.html", {
        "booking": booking
    })




def cancel_ticket(request):

    booking = None

    if request.method == "POST":

        pnr = request.POST.get("pnr")

        booking = booking_col.find_one({
            "pnr": int(pnr)
        })

        if "cancel" in request.POST and booking:

            booking_col.delete_one({
                "pnr": int(pnr)
            })

            return render(request,
                          "cancel.html",
                          {"success": True})

    return render(request,
                  "cancel.html",
                  {"booking": booking})



def my_bookings(request):

    bookings = []

    if request.method == "POST":

        mobile = request.POST.get("mobile")

        bookings = list(
            booking_col.find({
                "mobile": mobile
            })
        )

    return render(
        request,
        "history.html",
        {"bookings": bookings}
    )















def profile(request):

    email = request.session.get("email")

    if not email:
        return redirect("login")

    user = user_col.find_one({"email": email})

    if not user:
        return redirect("login")

    return render(request, "profile.html", {
        "name": user.get("name", ""),
        "email": user.get("email", ""),
        "dateofbirth": user.get("dateofbirth", ""),
        "gender": user.get("gender", ""),
        "phonenumber": user.get("phonenumber", ""),
        "address": user.get("address", ""),
        "city": user.get("city", ""),
        "state": user.get("state", ""),
        "pincode": user.get("pincode", ""),
    })









from django.shortcuts import render, redirect

def edit_profile(request):

    email = request.session.get("email")

    if not email:
        return redirect("login")

    user = user_col.find_one({"email": email})

    if not user:
        return redirect("login")

    if request.method == "POST":

        new_email = request.POST.get("email")
        password = request.POST.get("password")
        confirmpassword = request.POST.get("confirmpassword")

        # ✅ PASSWORD CHECK (IMPORTANT)
        if password != confirmpassword:
            return render(request, "edit_profile.html", {
                "error": "Password and Confirm Password do not match",
                "name": request.POST.get("name"),
                "email": request.POST.get("email"),
                "dateofbirth": request.POST.get("dateofbirth"),
                "gender": request.POST.get("gender"),
                "phonenumber": request.POST.get("phonenumber"),
                "address": request.POST.get("address"),
                "city": request.POST.get("city"),
                "state": request.POST.get("state"),
                "pincode": request.POST.get("pincode"),
            })

        result = user_col.update_one(
            {"email": email},
            {
                "$set": {
                    "name": request.POST.get("name"),
                    "email": new_email,
                    "dateofbirth": request.POST.get("dateofbirth"),
                    "gender": request.POST.get("gender"),
                    "phonenumber": request.POST.get("phonenumber"),
                    "address": request.POST.get("address"),
                    "city": request.POST.get("city"),
                    "state": request.POST.get("state"),
                    "pincode": request.POST.get("pincode"),
                    "password": password
                }
            }
        )

        print("Matched:", result.matched_count)
        print("Modified:", result.modified_count)

        # update session email if changed
        request.session["email"] = new_email

        return redirect("profile")

    return render(request, "edit_profile.html", {
        "name": user.get("name", ""),
        "email": user.get("email", ""),
        "dateofbirth": user.get("dateofbirth", ""),
        "gender": user.get("gender", ""),
        "phonenumber": user.get("phonenumber", ""),
        "address": user.get("address", ""),
        "city": user.get("city", ""),
        "state": user.get("state", ""),
        "pincode": user.get("pincode", "")
    })







def add_train(request):

    if request.method == "POST":

        train_no = request.POST.get("train_no")
        train_name = request.POST.get("train_name")
        source = request.POST.get("source")
        destination = request.POST.get("destination")
        departure_time = request.POST.get("departure_time")
        arrival_time = request.POST.get("arrival_time")
        ac_price = int(request.POST.get("ac_price"))
        sl_price = int(request.POST.get("sl_price"))
        ac_seats = int(request.POST.get("ac_seats"))
        sl_seats = int(request.POST.get("sl_seats"))

        col.insert_one({
            "train_no": train_no,
            "train_name": train_name,
            "source": source,
            "destination": destination,
            "departure_time": departure_time,
            "arrival_time": arrival_time,
            "ac_price": ac_price,
            "sl_price": sl_price,
            "ac_seats": ac_seats,
            "sl_seats": sl_seats
        })

        return HttpResponse("Train Added Successfully")

    return render(request, "add_train.html")








from django.shortcuts import render, redirect

def search_trains(request):

    # Check if user is logged in
    if "email" not in request.session:
        return redirect("login")

    if request.method == "POST":

        source = request.POST.get("source")
        destination = request.POST.get("destination")
        journey_date = request.POST.get("journey_date")

        print("Source:", source)
        print("Destination:", destination)

        trains = list(col.find({
            "source": source,
            "destination": destination
        }))

        for train in trains:
            train["id"] = str(train["_id"])

        return render(request, "results.html", {
            "trains": trains,
            "journey_date": journey_date
        })

    return redirect("/") 







def ticket(request):

    passengers = request.session.get("passengers", [])

    context = {
        "pnr": request.session.get("pnr"),
        "train_name": request.session.get("train_name"),
        "source": request.session.get("source"),
        "destination": request.session.get("destination"),
        "selected_class": request.session.get("travel_class"),
        "journey_date": request.session.get("journey_date"),
        "total_price": request.session.get("total_price"),
        "passengers": passengers,
    }

    # Clear passengers after showing ticket
    request.session["passengers"] = []
    request.session.pop("current_train", None)
    request.session.modified = True

    return render(request, "ticket.html", context)







from bson.objectid import ObjectId
import random
from django.shortcuts import redirect
from django.http import HttpResponse

def payment_process(request):

    if request.method == "POST":

        payment = request.POST.get("payment_method")

        # Net Banking
        if payment == "net banking":
            return redirect("net_banking")

        # Credit Card
        elif payment == "credit card":
            return redirect("credit_card")

        # UPI Payments
        elif payment in ["GPay", "PhonePe", "Paytm"]:

            request.session["payment_method"] = payment

            train_id = request.session.get("train_id")

            if not train_id:
                return HttpResponse("Train ID not found.")

            train = col.find_one({"_id": ObjectId(train_id)})

            if not train:
                return HttpResponse("Train not found.")

            passengers = request.session.get("passengers", [])
            total_passengers = len(passengers)

            selected_class = request.session.get("selected_class")

            print("Selected Class =", selected_class)

            if not selected_class:
                return HttpResponse("Class not found in session.")

            pnr = random.randint(1000000000, 9999999999)

            # ==========================
            # Coach Allocation
            # ==========================

            # if selected_class == "SL":
            #     coach = "S1"

            # elif selected_class == "3AC":
            #     coach = "B1"

            # elif selected_class == "2AC":
            #     coach = "A1"

            # elif selected_class == "1AC":
            #     coach = "H1"

            # else:
            #     coach = "S1"

            # print("Coach =", coach)



            
            
            if selected_class == "SL":
             coach = random.choice(["S1","S2","S3","S4","S5","S6","S7","S8","S9","S10"])
            
            elif selected_class == "3AC":
             coach = random.choice(["B1","B2","B3","B4"])
            
            elif selected_class == "2AC":
             coach = random.choice(["A1","A2"])
            
            elif selected_class == "1AC":
             coach = random.choice(["H1","H2"])
            
                        
            
            

            # ==========================
            # Seat Allocation
            # ==========================

            for passenger in passengers:

                passenger["coach"] = coach
                passenger["seat"] = random.randint(1, 72)
                passenger["berth"] = passenger.get(
                    "berth_preference",
                    "No Preference"
                )

            print(passengers)

            # ==========================
            # SAVE BOOKING
            # ==========================

            booking_col.insert_one({

                "pnr": pnr,
                "train_id": train_id,
                "train_name": train["train_name"],
                "source": train["source"],
                "destination": train["destination"],
                "class": selected_class,
                "journey_date": request.session.get("journey_date"),
                "total_price": request.session.get("total_price"),
                "mobile": request.session.get("mobile"),
                "payment_method": payment,
                "passengers": passengers

            })

            # ==========================
            # UPDATE AVAILABLE SEATS
            # ==========================

            col.update_one(
                {"_id": ObjectId(train_id)},
                {
                    "$inc": {
                        f"seats.{selected_class}": -total_passengers
                    }
                }
            )

            # ==========================
            # SAVE SESSION
            # ==========================

            request.session["pnr"] = pnr
            request.session["passengers"] = passengers
            request.session["train_name"] = train["train_name"]
            request.session["source"] = train["source"]
            request.session["destination"] = train["destination"]
            request.session["travel_class"] = selected_class

            return redirect("ticket")

    return redirect("payment")






from django.shortcuts import render, redirect
from django.http import HttpResponse
from bson.objectid import ObjectId
import random

def net_banking(request):

    if request.method == "POST":

        train_id = request.session.get("train_id")

        if not train_id:
            return HttpResponse("Train not found.")

        train = col.find_one({"_id": ObjectId(train_id)})

        if not train:
            return HttpResponse("Train not found.")

        passengers = request.session.get("passengers", [])

        if not passengers:
            return HttpResponse("No passengers found.")

        selected_class = request.session.get("travel_class")

        pnr = random.randint(1000000000, 9999999999)

        # ==========================
        # Coach Allocation
        # ==========================

        if selected_class == "SL":
            coach = "S1"

        elif selected_class == "3AC":
            coach = "B1"

        elif selected_class == "2AC":
            coach = "A1"

        elif selected_class == "1AC":
            coach = "H1"

        else:
            coach = "S1"

        # ==========================
        # Seat Allocation
        # ==========================

        for passenger in passengers:

            passenger["coach"] = coach
            passenger["seat"] = random.randint(1, 72)
            passenger["berth"] = passenger.get(
                "berth_preference",
                "No Preference"
            )

        # ==========================
        # Save Booking
        # ==========================

        booking_col.insert_one({

            "pnr": pnr,
            "train_id": train_id,
            "train_name": train["train_name"],
            "source": train["source"],
            "destination": train["destination"],
            "class": selected_class,
            "journey_date": request.session.get("journey_date"),
            "mobile": request.session.get("mobile"),
            "payment_method": "Net Banking",
            "total_price": request.session.get("total_price"),
            "passengers": passengers

        })

        # ==========================
        # Reduce Seats
        # ==========================

        col.update_one(
            {"_id": ObjectId(train_id)},
            {
                "$inc": {
                    f"seats.{selected_class}": -len(passengers)
                }
            }
        )

        # ==========================
        # Save Session
        # ==========================

        request.session["pnr"] = pnr
        request.session["train_name"] = train["train_name"]
        request.session["source"] = train["source"]
        request.session["destination"] = train["destination"]
        request.session["passengers"] = passengers

        request.session.pop("current_train", None)
        request.session.modified = True

        return redirect("ticket")

    return render(request, "net_banking.html", {
        "total_price": request.session.get("total_price")
    })



















from django.shortcuts import render, redirect
from django.http import HttpResponse
from bson.objectid import ObjectId
import random

def credit_card(request):

    if request.method == "POST":

        train_id = request.session.get("train_id")

        if not train_id:
            return HttpResponse("Train not found.")

        train = col.find_one({"_id": ObjectId(train_id)})

        if not train:
            return HttpResponse("Train not found.")

        passengers = request.session.get("passengers", [])

        if not passengers:
            return HttpResponse("No passengers found.")

        selected_class = request.session.get("travel_class")

        pnr = random.randint(1000000000, 9999999999)

        # ==========================
        # Coach Allocation
        # ==========================

        if selected_class == "SL":
            coach = "S1"

        elif selected_class == "3AC":
            coach = "B1"

        elif selected_class == "2AC":
            coach = "A1"

        elif selected_class == "1AC":
            coach = "H1"

        else:
            coach = "S1"

        # ==========================
        # Seat Allocation
        # ==========================

        for passenger in passengers:

            passenger["coach"] = coach
            passenger["seat"] = random.randint(1, 72)
            passenger["berth"] = passenger.get(
                "berth_preference",
                "No Preference"
            )

        # ==========================
        # Save Booking
        # ==========================

        booking_col.insert_one({

            "pnr": pnr,
            "train_id": train_id,
            "train_name": train["train_name"],
            "source": train["source"],
            "destination": train["destination"],
            "class": selected_class,
            "journey_date": request.session.get("journey_date"),
            "mobile": request.session.get("mobile"),
            "payment_method": "Credit Card",
            "total_price": request.session.get("total_price"),
            "passengers": passengers

        })

        # ==========================
        # Reduce Seats
        # ==========================

        col.update_one(

            {"_id": ObjectId(train_id)},

            {
                "$inc": {
                    f"seats.{selected_class}": -len(passengers)
                }
            }

        )

        # ==========================
        # Save Session
        # ==========================

        request.session["pnr"] = pnr
        request.session["train_name"] = train["train_name"]
        request.session["source"] = train["source"]
        request.session["destination"] = train["destination"]
        request.session["passengers"] = passengers
        request.session["travel_class"] = selected_class

        request.session.pop("current_train", None)
        request.session.modified = True

        return redirect("ticket")

    return render(request, "credit_card.html", {
        "total_price": request.session.get("total_price")
    })






































from django.shortcuts import render, redirect
from django.http import HttpResponse
from bson.objectid import ObjectId
import random

def book_train(request, train_id):

    # ===============================
    # GET TRAIN DETAILS
    # ===============================

    train = col.find_one({"_id": ObjectId(train_id)})

    if not train:
        return HttpResponse("Train Not Found")

    selected_class = request.GET.get("class")

    if not selected_class:
        selected_class = request.session.get("selected_class", "SL")

    journey_date = request.GET.get("journey_date")

    if journey_date:
        request.session["journey_date"] = journey_date
    else:
        journey_date = request.session.get("journey_date")

    # ===============================
    # START NEW BOOKING
    # ===============================

    if request.method == "GET":

        current_train = request.session.get("current_train")

        if current_train != train_id:

            request.session["passengers"] = []
            request.session["current_train"] = train_id

            request.session.pop("captcha", None)
            request.session.pop("mobile", None)

            request.session.modified = True

    passengers = request.session.get("passengers", [])


    print("TRAIN ID:", train_id)
    print("CURRENT TRAIN:", request.session.get("current_train"))
    print("SESSION PASSENGERS:", request.session.get("passengers"))
    print("PASSENGERS VARIABLE:", passengers)

    # ===============================
    # POST REQUEST
    # ===============================

    if request.method == "POST":

        # ===========================
        # ADD PASSENGER
        # ===========================

        if "add" in request.POST:

            passenger = {

                "name": request.POST.get("name"),
                "age": request.POST.get("age"),
                "gender": request.POST.get("gender"),
                "berth_preference": request.POST.get("berth_preference")

            }

            passengers.append(passenger)

            request.session["passengers"] = passengers
            request.session.modified = True

            return redirect(
                f"/book/{train_id}/?class={selected_class}&journey_date={journey_date}"
            )

        # ===========================
        # DELETE PASSENGER
        # ===========================

        elif "delete" in request.POST:

            index = int(request.POST.get("delete_index"))

            if 0 <= index < len(passengers):
                passengers.pop(index)

            request.session["passengers"] = passengers
            request.session.modified = True

            return redirect(
                f"/book/{train_id}/?class={selected_class}&journey_date={journey_date}"
            )



            

        # =========================
        # CONFIRM BOOKING
        # =========================

        elif "confirm" in request.POST:

            if len(passengers) == 0:
                return HttpResponse("Please add at least one passenger.")

            # Get price and seats dynamically
            price = train["classes"].get(selected_class)
            available_seats = train["seats"].get(selected_class)

            if price is None or available_seats is None:
               return HttpResponse("Invalid Class Selected")

            total_passengers = len(passengers)
            total_price = price * total_passengers

            if total_passengers > available_seats:
                return HttpResponse("Not enough seats available.")
            



            request.session["train_id"] = str(train["_id"])      # <-- ADD THIS
            request.session["train_name"] = train["train_name"]  # <-- ADD THIS
            request.session["source"] = train["source"]          # <-- ADD THIS
            request.session["destination"] = train["destination"]










            request.session["selected_class"] = selected_class

            request.session["travel_class"] = selected_class  



            request.session["total_price"] = total_price
            request.session["total_passengers"] = total_passengers

            return render(request, "success.html", {
                "total_price": total_price,
                "total_passengers": total_passengers,
                "show_mobile": True
            })

        # =========================
        # SHOW CAPTCHA
        # =========================

        elif "showcaptcha" in request.POST:

            mobile = request.POST.get("mobile")

            captcha = random.randint(1000, 9999)

            request.session["captcha"] = captcha
            request.session["mobile"] = mobile

            return render(request, "success.html", {
                "mobile": mobile,
                "captcha": captcha,
                "show_captcha": True,
                "total_price": request.session.get("total_price"),
                "total_passengers": request.session.get("total_passengers")
            })

        # =========================
        # VERIFY CAPTCHA
        # =========================

        elif "verifycaptcha" in request.POST:

            user_captcha = request.POST.get("user_captcha")

            if str(user_captcha) == str(request.session.get("captcha")):

                return render(request, "payment.html", {
                    "total_price": request.session.get("total_price")
                })

            else:
                return HttpResponse("Invalid Captcha")

        # =========================
        # PAYMENT SUCCESS
        # =========================

        elif "payment" in request.POST:

            payment_method = request.POST.get("payment_method")

            total_price = request.session.get("total_price")
            total_passengers = request.session.get("total_passengers")

            pnr = random.randint(1000000000, 9999999999)

            for passenger in passengers:
                passenger["seat"] = random.randint(1, 72)
                passenger["berth"] = passenger["berth_preference"]
            




            if selected_class == "SL":
                coach = random.choice(["S1","S2","S3","S4","S5","S6","S7","S8","S9","S10"])

            elif selected_class == "3AC":
                coach = random.choice(["B1","B2","B3","B4"])

            elif selected_class == "2AC":
                coach = random.choice(["A1","A2"])

            elif selected_class == "1AC":
                coach = random.choice(["H1","H2"])

            for passenger in passengers:
                passenger["coach"] = coach
                passenger["seat"] = random.randint(1, 72)
                passenger["berth"] = passenger["berth_preference"]














        


            booking_col.insert_one({

                "pnr": pnr,
                "train_id": train_id,
                "train_name": train["train_name"],
                "source": train["source"],
                "destination": train["destination"],
                "class": selected_class,
                "payment_method": payment_method,
                "journey_date": request.session.get("journey_date"),
                "mobile": request.session.get("mobile"),
                "total_price": total_price,
                "passengers": passengers

            })

            col.update_one(
                   {"_id": ObjectId(train_id)},
    {
        "$inc": {
            f"seats.{selected_class}": -total_passengers
        }
    }
)

            # CLEAR SESSION PASSENGERS

            request.session["passengers"] = []
            request.session.pop("current_train", None)
            request.session.modified = True

            return render(request, "ticket.html", {

                "pnr": pnr,
                "train": train,
                "passengers": passengers,
                "selected_class": selected_class,
                "journey_date": request.session.get("journey_date"),
                "payment_method": payment_method,
                "mobile": request.session.get("mobile"),
                "total_price": total_price

            })

    # =========================
    # BOOK PAGE
    # =========================

    return render(request, "book.html", {

        "train": train,
        "passengers": passengers,
        "selected_class": selected_class,
        "journey_date": journey_date

    })








