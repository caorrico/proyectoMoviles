import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter/material.dart';
import 'theme.dart';
import 'widgets/service_card.dart';
import 'widgets/chat_widget.dart';
Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await dotenv.load();
  final serverIp = dotenv.env['SERVER_IP'] ?? '10.0.2.2';
  runApp(MyApp(serverIp: serverIp));
}

class MyApp extends StatelessWidget {
  final String serverIp;
  const MyApp({Key? key, required this.serverIp}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Municipio Digital',
      theme: appTheme,
      home: HomePage(serverIp: serverIp),
    );
  }
}



class HomePage extends StatefulWidget {
  final String serverIp;
  const HomePage({Key? key, required this.serverIp}) : super(key: key);

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  bool _showChat = false;

  void _openChat() {
    setState(() {
      _showChat = true;
    });
  }

  void _closeChat() {
    setState(() {
      _showChat = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        Scaffold(
          backgroundColor: Colors.grey[100],
          body: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Encabezado institucional
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.only(top: 48, bottom: 24),
                  decoration: const BoxDecoration(
                    color: AppColors.primary,
                    borderRadius: BorderRadius.only(
                      bottomLeft: Radius.circular(32),
                      bottomRight: Radius.circular(32),
                    ),
                  ),
                  child: Column(
                    children: [
                      Text(
                        'MUNICIPIO DIGITAL',
                        style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                            ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Gobierno Autónomo Descentralizado',
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              color: Colors.white70,
                            ),
                      ),
                      const SizedBox(height: 16),
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 24),
                        child: Container(
                          padding: const EdgeInsets.all(24),
                          decoration: BoxDecoration(
                            color: AppColors.primaryDark,
                            borderRadius: BorderRadius.circular(24),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('Bienvenido al Portal Ciudadano',
                                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(color: Colors.white)),
                              const SizedBox(height: 10),
                              const Text(
                                'Accede a todos los servicios municipales de forma rápida y sencilla. Nuestro asistente virtual está disponible 24/7 para ayudarte.',
                                style: TextStyle(color: Colors.white, fontSize: 16),
                              ),
                              const SizedBox(height: 18),
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                                children: [
                                  Expanded(
                                    child: OutlinedButton.icon(
                                      style: OutlinedButton.styleFrom(
                                        foregroundColor: Colors.white,
                                        side: const BorderSide(color: Colors.white),
                                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 12),
                                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
                                      ),
                                      icon: const Icon(Icons.info_outline),
                                      label: const Text('Información de Trámites'),
                                      onPressed: null, // Solo informativo
                                    ),
                                  ),
                                  const SizedBox(width: 12),
                                  Expanded(
                                    child: OutlinedButton.icon(
                                      style: OutlinedButton.styleFrom(
                                        foregroundColor: Colors.white,
                                        side: const BorderSide(color: Colors.white),
                                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 12),
                                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
                                      ),
                                      icon: const Icon(Icons.phone),
                                      label: const Text('Contacto'),
                                      onPressed: null, // Solo informativo
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 28),
                // Servicios destacados
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: Text('Servicios Más Consultados', style: Theme.of(context).textTheme.labelLarge),
                ),
                const SizedBox(height: 12),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 8),
                  child: Column(
                    children: [
                      ServiceCard(
                        icon: Icons.home_repair_service,
                        title: 'Permisos de Construcción',
                        description: 'Solicita permisos para obra nueva, ampliación o refacción',
                      ),
                      ServiceCard(
                        icon: Icons.receipt_long,
                        title: 'Impuestos y Tasas',
                        description: 'Pago de impuestos municipales y consulta de deudas',
                      ),
                      ServiceCard(
                        icon: Icons.calendar_month,
                        title: 'Turnos Online',
                        description: 'Reserva tu turno para atención presencial',
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 28),
              ],
            ),
          ),
          floatingActionButton: FloatingActionButton(
            backgroundColor: AppColors.primary,
            child: const Icon(Icons.android),
            onPressed: _openChat,
          ),
        ),
        if (_showChat)
          ChatWidget(onClose: _closeChat, serverIp: widget.serverIp),
      ],
    );
  }
}

