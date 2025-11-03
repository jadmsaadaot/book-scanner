import { Badge } from "@chakra-ui/react"

interface MatchBadgeProps {
  score: number // 0-1 or 0-100
  size?: "sm" | "md" | "lg"
}

/**
 * MatchBadge component to display recommendation match score
 * Color-coded based on match percentage
 */
const MatchBadge = ({ score, size = "md" }: MatchBadgeProps) => {
  // Convert to percentage if needed (assume 0-1 if score <= 1)
  const percentage = score <= 1 ? Math.round(score * 100) : Math.round(score)

  // Determine color based on score
  const getColorScheme = (pct: number) => {
    if (pct >= 90) return "green"
    if (pct >= 75) return "blue"
    if (pct >= 60) return "yellow"
    return "gray"
  }

  const colorScheme = getColorScheme(percentage)

  return (
    <Badge colorScheme={colorScheme} size={size} variant="solid">
      {percentage}% Match
    </Badge>
  )
}

export default MatchBadge
