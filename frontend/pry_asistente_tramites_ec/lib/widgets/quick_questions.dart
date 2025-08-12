import 'package:flutter/material.dart';
import '../theme.dart';

class QuickQuestions extends StatelessWidget {
  final void Function(String) onQuestionSelected;
  const QuickQuestions({super.key, required this.onQuestionSelected});

  @override
  Widget build(BuildContext context) {
    final questions = [
      '¿Cómo saco un permiso de construcción?',
      '¿Cuáles son los requisitos para recolección de residuos?',
      '¿Cómo pago mis impuestos municipales?',
      '¿Cómo reservo un turno online?',
      '¿Dónde encuentro información de trámites?',
    ];
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: questions.map((q) => ElevatedButton.icon(
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.primary,
          foregroundColor: Colors.white,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
        ),
        icon: const Icon(Icons.question_answer),
        label: Text(q, style: const TextStyle(fontSize: 14)),
        onPressed: () => onQuestionSelected(q),
      )).toList(),
    );
  }
}
