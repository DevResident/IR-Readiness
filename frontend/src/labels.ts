// Display labels for enum values coming from the API.

export function humanize(value: string): string {
  const text = value.replaceAll('_', ' ')
  return text.charAt(0).toUpperCase() + text.slice(1)
}

export const ORG_SIZE_LABELS: Record<string, string> = {
  small: 'Small (under 250 employees)',
  medium: 'Medium (250 to 2,500 employees)',
  large: 'Large (over 2,500 employees)',
}

export const AUDIENCE_LABELS: Record<string, string> = {
  technical: 'Technical (IT and security staff)',
  executive: 'Executive (leadership and business owners)',
}
