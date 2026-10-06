import { useState, type FormEvent } from "react";

type InviteMemberFormProps = {
  onInvite: (email: string, role: string) => Promise<void>;
};

const InviteMemberForm = ({ onInvite }: InviteMemberFormProps) => {
  const [email, setEmail] = useState<string>("");
  const [role, setRole] = useState<string>("Viewer");
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!email.trim()) return;

    setIsSubmitting(true);
    try {
      await onInvite(email.trim(), role);
      setEmail("");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex items-center gap-2">
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email address"
        className="flex-1 px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900"
      />
      <select
        value={role}
        onChange={(e) => setRole(e.target.value)}
        className="px-3 py-2 text-sm border border-slate-300 rounded-lg cursor-pointer focus:outline-none focus:ring-2 focus:ring-slate-900"
      >
        <option value="Viewer">Viewer</option>
        <option value="Admin">Admin</option>
      </select>
      <button
        type="submit"
        disabled={isSubmitting || !email.trim()}
        className="px-3.5 py-2 text-sm font-medium rounded-lg bg-slate-900 text-white hover:bg-slate-800 transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Invite
      </button>
    </form>
  );
};

export default InviteMemberForm;
