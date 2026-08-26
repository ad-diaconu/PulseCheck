import { useState, type SubmitEvent } from "react";
import { Link } from "react-router-dom";
import { ArrowRight } from "lucide-react";
import { GoogleIcon } from "../components/GoogleIcon";

const LoginForm = () => {

    const [isLoading, setIsLoading] = useState(false);
    const handleSubmit = (e: SubmitEvent<HTMLFormElement>) => {
        e.preventDefault()
        setIsLoading(true);
        //login logic call login api
    }

    return (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8">

            {/* Header */}
            <div className="flex flex-col gap-1 mb-8 text-center">
                <h1 className="text-2xl font-bold text-slate-900">
                    Welcome back
                </h1>
                <p className="text-sm text-slate-500">
                    Sign in to your account
                </p>
            </div>

            {/* Formular */}
            <form onSubmit={handleSubmit} className="flex flex-col gap-5">

                {/* Email */}
                <div className="flex flex-col gap-1.5">
                    <label htmlFor="email" className="text-sm font-medium text-slate-700">
                        Email
                    </label>
                    <input
                        type="email"
                        id="email"
                        placeholder="you@company.com"
                        className="w-full p-2.5 rounded-lg border border-slate-300 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow"
                    />
                </div>

                {/* Password */}
                <div className="flex flex-col gap-1.5">
                    <div className="flex items-center justify-between">
                        <label htmlFor="password" className="text-sm font-medium text-slate-700">
                            Password
                        </label>
                        <Link to="/auth/recovery" className="text-sm text-slate-500 hover:text-blue-600 hover:underline">
                            Forgot password?
                        </Link>
                    </div>
                    <input
                        type="password"
                        id="password"
                        placeholder="••••••••"
                        autoComplete="current-password"
                        className="w-full p-2.5 rounded-lg border border-slate-300 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow"
                    />
                </div>

                {/* Submit Button */}
                <button
                    type="submit"
                    disabled={isLoading}
                    className="w-full flex items-center justify-center gap-2 bg-slate-900 text-white font-medium text-sm p-2.5 rounded-lg hover:bg-slate-800 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 cursor-pointer disabled:cursor-not-allowed disabled:opacity-70"
                >
                    {isLoading ? 'Loading...' : (
                        <>
                            Sign In
                            <ArrowRight className="w-4 h-4" />
                        </>
                    )}
                </button>
            </form>

            {/*Divider*/}
            <div className="relative my-6">
                <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-slate-200"></div>
                </div>
                <div className="relative flex justify-center text-xs">
                    <span className="bg-white px-3 text-slate-400 uppercase tracking-wider">
                        Or continue with
                    </span>
                </div>
            </div>

            {/* Google Button */}
            <button
                type="button"
                className="w-full flex items-center justify-center gap-3 p-2.5 rounded-lg border border-slate-300 bg-white text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1"
            >
                <GoogleIcon className="w-5 h-5" />
                Continue with Google
            </button>

            {/* Footer */}
            <div className="mt-8 text-center text-sm text-slate-500">
                Don't have an account?{' '}
                <Link to="/auth/signup" className="text-slate-800 font-semibold hover:underline">
                    Sign up
                </Link>
            </div>


        </div>
    );
}

export default LoginForm;