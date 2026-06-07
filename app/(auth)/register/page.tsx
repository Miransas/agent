"use client";

import { useState } from "react";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

import { AuthBrandPanel } from "@/components/auth/auth-brand-panel";
import { Logomark } from "@/components/brand/logomark";
import { useAuth } from "@/components/provider/auth-provider";
import { ApiError } from "@/lib/api";
import Image from "next/image";

const registerSchema = z.object({
  email: z.string().email("Please enter a valid email"),
  password: z.string().min(8, "Password must be at least 8 characters"),
  name: z
    .string()
    .max(200, "Name must be 200 characters or fewer")
    .optional()
    .or(z.literal("")),
});

type RegisterFormData = z.infer<typeof registerSchema>;

const inputClass =
  "w-full rounded-lg border border-white/[0.08] bg-white/[0.02] px-4 py-3 text-sm text-foreground placeholder:text-zinc-500 transition-colors focus:border-[#8CFF2E]/40 focus:outline-none focus:ring-2 focus:ring-[#8CFF2E]/10";

export default function RegisterPage() {
  const { register: registerUser } = useAuth();
  const [serverError, setServerError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterFormData) => {
    setServerError(null);
    try {
      await registerUser(
        data.email,
        data.password,
        data.name?.trim() || undefined
      );
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.status === 409) {
          setServerError("An account with this email already exists.");
        } else {
          setServerError(err.message || "Registration failed");
        }
      } else {
        setServerError("Something went wrong. Please try again.");
      }
    }
  };

  return (
    <div className="grid min-h-screen md:grid-cols-2">
      <AuthBrandPanel variant="register" />

      <div className="flex items-center justify-center bg-[#050505] p-6 md:p-12">
        <div className="w-full max-w-md space-y-8">
          <div className="mb-8 flex items-center gap-3 md:hidden">
            <Image src="/favicon/favicon.svg" alt="CourierX" width={32} height={32} />
            <span className="text-lg font-bold text-foreground">CourierX</span>
          </div>

          <div className="space-y-2">
            <h2 className="text-3xl font-bold tracking-tight text-foreground">
              Create your account
            </h2>
            <p className="text-base text-zinc-400">
              Start sending email from your own infrastructure.
            </p>
          </div>

          <form
            onSubmit={handleSubmit(onSubmit)}
            className="space-y-5"
            noValidate
          >
            <div>
              <label
                htmlFor="email"
                className="mb-1.5 block text-xs font-medium text-zinc-400"
              >
                Email
              </label>
              <input
                id="email"
                type="email"
                autoComplete="email"
                placeholder="you@company.com"
                aria-invalid={errors.email ? true : undefined}
                className={inputClass}
                {...register("email")}
              />
              {errors.email ? (
                <p className="mt-1.5 text-xs text-red-400">
                  {errors.email.message}
                </p>
              ) : null}
            </div>

            <div>
              <label
                htmlFor="password"
                className="mb-1.5 block text-xs font-medium text-zinc-400"
              >
                Password
              </label>
              <input
                id="password"
                type="password"
                autoComplete="new-password"
                placeholder="••••••••"
                aria-invalid={errors.password ? true : undefined}
                className={inputClass}
                {...register("password")}
              />
              {errors.password ? (
                <p className="mt-1.5 text-xs text-red-400">
                  {errors.password.message}
                </p>
              ) : (
                <p className="mt-1.5 text-xs text-zinc-500">
                  At least 8 characters.
                </p>
              )}
            </div>

            <div>
              <label
                htmlFor="name"
                className="mb-1.5 flex items-center justify-between text-xs font-medium text-zinc-400"
              >
                <span>Name</span>
                <span className="text-zinc-600">optional</span>
              </label>
              <input
                id="name"
                type="text"
                autoComplete="name"
                placeholder="Ada Lovelace"
                aria-invalid={errors.name ? true : undefined}
                className={inputClass}
                {...register("name")}
              />
              {errors.name ? (
                <p className="mt-1.5 text-xs text-red-400">
                  {errors.name.message}
                </p>
              ) : null}
            </div>

            {serverError ? (
              <div
                role="alert"
                className="rounded-lg border border-red-500/20 bg-red-500/5 px-4 py-3"
              >
                <p className="text-sm text-red-400">{serverError}</p>
              </div>
            ) : null}

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full rounded-full bg-[#8CFF2E] px-6 py-3 font-semibold text-[#050505] shadow-[0_0_30px_-8px_rgba(140,255,46,0.4)] transition-colors hover:bg-[#8CFF2E]/90 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isSubmitting ? "Creating…" : "Create account"}
            </button>
          </form>

          <p className="text-center text-sm text-zinc-500">
            Already have an account?{" "}
            <Link
              href="/login"
              className="font-medium text-foreground transition-colors hover:text-[#8CFF2E]"
            >
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
