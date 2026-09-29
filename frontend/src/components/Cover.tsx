export function Cover({ name, label }: { name: string; label?: string }) {
  return (
    <div className={`cover cover-${name}`}>
      <span>{label}</span>
    </div>
  );
}
