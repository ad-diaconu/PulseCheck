
import { type ReactNode } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react"

const AuthLayout = () => {
    const navigate = useNavigate();

    return (

        <div className="min-h-screen relative flex flex-col items-center justify-center bg-slate-50 p-4">
            <button
                type="button"
                onClick={() => navigate("/")}
                className="absolute top-6 left-6 flex items-center gap-2 text-sm font-medium text-slate-500 hover:text-slate-900 cursor-pointer transition-colors">
                <ArrowLeft className="w-4 h-4" />
                Back
            </button>

            {/* logo */}
            <div className="mb-8 flex items-center justify-center gap-2">
                <div className="w-8 h-8 bg-slate-800 rounded flex items-center justify-center">
                    <span className="text-white font-bold text-xl">P</span>
                </div>
                <span className="text-2xl font-bold text-slate-900 tracking-tight">PulseCheck</span>
            </div>

            <div className="w-full max-w-md">
                <Outlet />
            </div>
        </div>
    );
}

export default AuthLayout;