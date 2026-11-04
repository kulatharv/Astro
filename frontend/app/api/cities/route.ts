import { NextResponse } from 'next/server';

const FALLBACK_CITIES = [
  "Delhi", "New Delhi", "Mumbai", "Bengaluru", "Kolkata", "Chennai", "Hyderabad",
  "Pune", "Ahmedabad", "Jaipur", "Lucknow", "Chandigarh", "Varanasi", "Surat",
  "Indore", "Nagpur", "Bhopal", "Patna", "Vadodara", "Coimbatore", "Ludhiana",
  "Agra", "Nashik", "Faridabad", "Meerut", "Rajkot", "Kalyan", "Thane", "Amritsar",
  "Allahabad", "Prayagraj", "Visakhapatnam", "Jabalpur", "Gwalior", "Vijayawada",
  "Jodhpur", "Madurai", "Raipur", "Kota", "Guwahati", "Ranchi", "London", "New York",
  "Dubai", "Singapore", "Kathmandu", "Toronto", "Sydney"
];

export async function GET() {
  try {
    const backendUrl = process.env.BACKEND_API_URL || 'http://127.0.0.1:8000';
    const response = await fetch(`${backendUrl}/api/cities`, {
      signal: AbortSignal.timeout(5000),
      next: { revalidate: 86400 }, // Cache for 24h
    });

    if (response.ok) {
      const data = await response.json();
      return NextResponse.json(data);
    }
    return NextResponse.json(FALLBACK_CITIES);
  } catch (err) {
    return NextResponse.json(FALLBACK_CITIES);
  }
}

