import { Loader2 } from "lucide-react";
import { cn } from "../../lib/format";

export default function Spinner({ className }) {
  return (
    <Loader2 aria-hidden="true" className={cn("size-4 animate-spin", className)} />
  );
}
