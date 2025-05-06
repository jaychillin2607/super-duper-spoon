import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const validateTIN = (tin: string) => {
  // Simple validation for SSN (XXX-XX-XXXX) or EIN (XX-XXXXXXX)
  const tinRegex = /^(\d{3}-\d{2}-\d{4}|\d{2}-\d{7})$/;
  return tinRegex.test(tin);
};

export const validateZipCode = (zipCode: string) => {
  const zipRegex = /^\d{5}(-\d{4})?$/;
  return zipRegex.test(zipCode);
};

export const validateEmail = (email: string) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const validatePhone = (phone: string) => {
  const phoneRegex = /^\d{10}$/;
  return phoneRegex.test(phone.replace(/\D/g, ""));
};
