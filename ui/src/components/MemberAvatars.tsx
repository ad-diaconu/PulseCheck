import type { Member } from "../types/member";

type MemberAvatarsProps = {
  members: Member[];
  maxVisible?: number;
};

const AVATAR_COLORS = [
  "bg-slate-700",
  "bg-emerald-600",
  "bg-amber-600",
  "bg-sky-600",
  "bg-rose-600",
];

function getColor(index: number) {
  return AVATAR_COLORS[index % AVATAR_COLORS.length];
}

function getInitial(email: string) {
  return email.slice(0, 1).toUpperCase();
}

const MemberAvatars = ({ members, maxVisible = 4 }: MemberAvatarsProps) => {
  const visible = members.slice(0, maxVisible);
  const overflow = members.length - visible.length;

  if (members.length === 0) {
    return <p className="text-xs text-slate-400">No members</p>;
  }

  return (
    <div className="flex items-center -space-x-2">
      {visible.map((member, index) => (
        <div
          key={member.user_id}
          title={`${member.email} (${member.role})`}
          className={`size-7 rounded-full flex items-center justify-center text-xs font-medium text-white ring-2 ring-white ${getColor(index)}`}
        >
          {getInitial(member.email)}
        </div>
      ))}
      {overflow > 0 && (
        <div className="size-7 rounded-full flex items-center justify-center text-xs font-medium text-slate-600 bg-slate-100 ring-2 ring-white">
          +{overflow}
        </div>
      )}
    </div>
  );
};

export default MemberAvatars;
