import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-primary text-primary-foreground",
        secondary:
          "border-transparent bg-secondary text-secondary-foreground",
        destructive:
          "border-transparent bg-red-600/20 text-red-400 border-red-600/30",
        outline:
          "border-white/10 text-white/70",
        telegram:
          "border-transparent bg-sky-500/20 text-sky-400 border-sky-500/30",
        discord:
          "border-transparent bg-indigo-500/20 text-indigo-400 border-indigo-500/30",
        fire:
          "border-transparent bg-orange-500/20 text-orange-400 border-orange-500/30",
        hot:
          "border-transparent bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
        good:
          "border-transparent bg-green-500/20 text-green-400 border-green-500/30",
        purple:
          "border-transparent bg-purple-500/20 text-purple-400 border-purple-500/30",
        mercari:
          "border-transparent bg-red-500/20 text-red-400 border-red-500/30",
        yahoo:
          "border-transparent bg-purple-500/20 text-purple-400 border-purple-500/30",
      },
    },
    defaultVariants: { variant: "default" },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants }
