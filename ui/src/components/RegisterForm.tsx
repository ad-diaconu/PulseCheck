import { useState, type SubmitEvent } from "react";
import { Link } from "react-router-dom";
import { ArrowRight } from "lucide-react";
import { GoogleIcon } from "../components/GoogleIcon";
import FormAlert from "../components/FormAlert";

export type SignupData = {
    email: string;
    password: string;
}

type Props = {
    onSubmit: (data: SignupData, resetForm: () => void) => Promise<void>;
    error: string | null;
    successMessage: string | null;
}

const RegisterForm = ({ onSubmit, error, successMessage }: Props) => {

    const [isLoading, setIsLoading] = useState(false);
    const [validationError, setValidationError] = useState<string | null>(null);

    const handleSubmit = async (e: SubmitEvent<HTMLFormElement>) => {
        e.preventDefault()
        setValidationError(null);

        const form = e.currentTarget;
        const formData = new FormData(form);
        const email = formData.get('email') as string;
        const password = formData.get('password') as string;
        const confirmPassword = formData.get('confirmPassword') as string;

        const passwordRegex = /(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9])/;
        if (!passwordRegex.test(password)) {
            setValidationError("Password must contain at least one uppercase letter, one number, and one symbol.");
            return;
        }

        if (password != confirmPassword) {
            setValidationError("Passwords do not match.");
            return;
        }

        setIsLoading(true);
        await onSubmit({ email, password }, () => form.reset());
        setIsLoading(false);
    }

    const displayError = validationError || error;

    return (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8">

            {/* Header */}
            <div className="flex flex-col gap-1 mb-8 text-center">
                <h1 className="text-2xl font-bold text-slate-900">
                    Create your account
                </h1>
                <p className="text-sm text-slate-500">
                    Try our unlimited plan free for 7 days
                </p>
            </div>

            {/* Errors */}
            <FormAlert type="error" message={displayError} />
            <FormAlert type="success" message={successMessage} />


            {/* Formular */}
            <form onSubmit={handleSubmit} className="flex flex-col gap-5">

                {/* Name */}
                {/* <div className="flex flex-col gap-1.5">
                    <label htmlFor="name" className="text-sm font-medium text-slate-700">
                        Full Name
                    </label>
                    <input
                        type="name"
                        id="name"
                        placeholder="Pulse Check"
                        className="w-full p-2.5 rounded-lg border border-slate-300 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow"
                    />
                </div> */}

                {/* Email */}
                <div className="flex flex-col gap-1.5">
                    <label htmlFor="email" className="text-sm font-medium text-slate-700">
                        Email
                    </label>
                    <input
                        type="email"
                        id="email"
                        name="email"
                        placeholder="you@company.com"
                        required
                        className="w-full p-2.5 rounded-lg border border-slate-300 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow"
                    />
                </div>

                {/* Password */}
                <div className="flex flex-col gap-1.5">
                    <div className="flex items-center justify-between">
                        <label htmlFor="password" className="text-sm font-medium text-slate-700">
                            Password
                        </label>
                    </div>
                    <input
                        type="password"
                        id="password"
                        name="password"
                        autoComplete="new-password"
                        placeholder="••••••••"
                        className="w-full p-2.5 rounded-lg border border-slate-300 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow"
                    />
                    <p className="text-xs text-slate-500">
                        Must contain at least 1 uppercase letter, 1 number, and 1 symbol.
                    </p>
                </div>

                {/* Confirm Password */}
                <div className="flex flex-col gap-1.5">
                    <div className="flex items-center justify-between">
                        <label htmlFor="confirmPassword" className="text-sm font-medium text-slate-700">
                            Confirm Password
                        </label>
                    </div>
                    <input
                        type="password"
                        id="confirmPassword"
                        autoComplete="new-password"
                        name="confirmPassword"
                        placeholder="••••••••"
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
                            Create Account
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
                Already have an account?{' '}
                <Link to="/auth/login" className="text-slate-800 font-semibold hover:underline">
                    Sign in
                </Link>
            </div>


        </div>
    );
}

export default RegisterForm;