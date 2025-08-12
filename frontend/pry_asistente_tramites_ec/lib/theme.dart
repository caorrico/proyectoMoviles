import 'package:flutter/material.dart';

class AppColors {
  static const primary = Color(0xFF005fa3);
  static const primaryDark = Color(0xFF00447a);
  static const secondary = Color(0xFFF8F9FA);
  static const accent = Color(0xFF28a745);
  static const text = Color(0xFF333333);
  static const textLight = Color(0xFF666666);
}

final ThemeData appTheme = ThemeData(
  primaryColor: AppColors.primary,
  scaffoldBackgroundColor: Colors.white,
  fontFamily: 'Inter',
  colorScheme: ColorScheme.fromSwatch().copyWith(
    primary: AppColors.primary,
    secondary: AppColors.accent,
  ),
  appBarTheme: const AppBarTheme(
    backgroundColor: AppColors.primary,
    foregroundColor: Colors.white,
    elevation: 0,
  ),
  textTheme: const TextTheme(
    headlineLarge: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: AppColors.primary),
    bodyMedium: TextStyle(fontSize: 16, color: AppColors.text),
    labelLarge: TextStyle(fontSize: 18, fontWeight: FontWeight.w600, color: AppColors.primary),
  ),
);
