import { useState } from "react";
import { User, Mail, Lock } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";

export default function Signup() {

  const navigate = useNavigate();


  const [form, setForm] = useState({

    name: "",
    email: "",
    password: "",
    confirmPassword: "",

  });



  const [loading, setLoading] = useState(false);



  const handleChange = (e) => {

    setForm({

      ...form,

      [e.target.name]: e.target.value,

    });

  };




  const handleSignup = async (e) => {

    e.preventDefault();



    if (
      !form.name ||
      !form.email ||
      !form.password ||
      !form.confirmPassword
    ) {

      alert("Please fill all fields");
      return;

    }



    if (form.password !== form.confirmPassword) {

      alert("Passwords do not match");
      return;

    }



    setLoading(true);



    try {


      const response = await fetch(

        "http://127.0.0.1:8000/api/auth/register",

        {

          method: "POST",

          headers: {

            "Content-Type": "application/json",

          },


          body: JSON.stringify({

            name: form.name,

            email: form.email,

            password: form.password,

          }),

        }

      );




      const data = await response.json();



      if (!response.ok) {

        throw new Error(

          data.detail || "Registration failed"

        );

      }




      alert("Account created successfully 🎉");


      navigate("/login");



    } catch(error) {


      alert(error.message);


    } finally {


      setLoading(false);


    }


  };




  return (

    <div className="min-h-screen bg-slate-950 flex justify-center items-center">


      <div className="bg-slate-900 w-[450px] rounded-3xl shadow-2xl p-10">


        <h1 className="text-4xl font-bold text-center text-blue-500">

          AI MISINFO

        </h1>



        <p className="text-center text-gray-400 mt-3">

          Create Your Account

        </p>




        <form

          onSubmit={handleSignup}

          className="space-y-5 mt-8"

        >



          <div className="flex items-center bg-slate-800 rounded-xl px-4">

            <User className="text-gray-400" />


            <input

              type="text"

              name="name"

              placeholder="Full Name"

              className="bg-transparent outline-none w-full p-4 text-white"

              onChange={handleChange}

            />


          </div>





          <div className="flex items-center bg-slate-800 rounded-xl px-4">


            <Mail className="text-gray-400" />


            <input

              type="email"

              name="email"

              placeholder="Email"

              className="bg-transparent outline-none w-full p-4 text-white"

              onChange={handleChange}

            />


          </div>





          <div className="flex items-center bg-slate-800 rounded-xl px-4">


            <Lock className="text-gray-400" />


            <input

              type="password"

              name="password"

              placeholder="Password"

              className="bg-transparent outline-none w-full p-4 text-white"

              onChange={handleChange}

            />


          </div>





          <div className="flex items-center bg-slate-800 rounded-xl px-4">


            <Lock className="text-gray-400" />


            <input

              type="password"

              name="confirmPassword"

              placeholder="Confirm Password"

              className="bg-transparent outline-none w-full p-4 text-white"

              onChange={handleChange}

            />


          </div>





          <button

            disabled={loading}

            className="w-full bg-blue-600 hover:bg-blue-700 py-4 rounded-xl font-bold transition disabled:opacity-60"

          >

            {

              loading

              ?

              "Creating Account..."

              :

              "Create Account"

            }


          </button>



        </form>





        <p className="text-center text-gray-400 mt-6">

          Already have an account?

        </p>




        <div className="text-center mt-2">


          <Link

            to="/login"

            className="text-blue-400 hover:underline"

          >

            Login

          </Link>


        </div>



      </div>


    </div>

  );

}