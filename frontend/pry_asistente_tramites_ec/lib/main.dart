import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter/material.dart';
import 'theme.dart';
import 'widgets/service_card.dart';
import 'widgets/chat_widget.dart';
import 'widgets/animated_card.dart';
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
                // Banner institucional
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
                      const SizedBox(height: 6),
                      Text(
                        'Gobierno Autónomo Descentralizado',
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              color: Colors.white70,
                            ),
                      ),
                      const SizedBox(height: 18),
                      // Barra de búsqueda visual
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 16),
                        child: Container(
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(24),
                            boxShadow: [
                              BoxShadow(
                                color: Colors.black.withOpacity(0.05),
                                blurRadius: 8,
                                offset: const Offset(0, 2),
                              ),
                            ],
                          ),
                          child: TextField(
                            enabled: false,
                            decoration: InputDecoration(
                              hintText: 'Buscar trámites, servicios o información',
                              prefixIcon: Icon(Icons.search, color: AppColors.primaryDark),
                              border: InputBorder.none,
                              contentPadding: const EdgeInsets.symmetric(vertical: 16),
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: 18),
                      // Accesos rápidos
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                        children: [
                          QuickAccessButton(
                            icon: Icons.assignment,
                            label: 'Trámites',
                            color: AppColors.primaryDark,
                          ),
                          QuickAccessButton(
                            icon: Icons.account_balance,
                            label: 'Pagos',
                            color: AppColors.primaryDark,
                          ),
                          QuickAccessButton(
                            icon: Icons.info_outline,
                            label: 'Información',
                            color: AppColors.primaryDark,
                          ),
                        ],
                      ),
                      const SizedBox(height: 24),
                      // Tarjeta animada para los párrafos institucionales
                      AnimatedCard(
                        delay: 200,
                        child: Card(
                          elevation: 4,
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
                          child: Padding(
                            padding: const EdgeInsets.all(18.0),
                            child: Text(
                              'Nuestro compromiso es ofrecerte una experiencia digital segura, eficiente y cercana. ¡Gracias por confiar en nosotros! ',
                              style: Theme.of(context).textTheme.bodyMedium,
                              textAlign: TextAlign.justify,
                            ),
                          ),
                        ),
                      ),
                      // Avisos o noticias destacadas
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 16),
                        child: Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: Colors.blue[50],
                            borderRadius: BorderRadius.circular(14),
                          ),
                          child: Row(
                            children: [
                              Icon(Icons.campaign, color: AppColors.primaryDark),
                              const SizedBox(width: 10),
                              Expanded(
                                child: Text(
                                  '¡Recuerda! Puedes realizar tus trámites en línea y evitar filas.',
                                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.w500),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),

                // Servicios más consultados
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 18),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Servicios más consultados',
                        style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                              color: AppColors.primaryDark,
                              fontWeight: FontWeight.bold,
                            ),
                      ),
                      const SizedBox(height: 12),
                      Column(
                        children: const [
                          ServiceCard(
                            icon: Icons.credit_card,
                            title: 'Pago de impuestos',
                            description: 'Consulta y paga tus impuestos municipales en línea.',
                          ),
                          SizedBox(height: 12),
                          ServiceCard(
                            icon: Icons.home_work,
                            title: 'Certificado de predio',
                            description: 'Solicita tu certificado de predio de manera digital.',
                          ),
                          SizedBox(height: 12),
                          ServiceCard(
                            icon: Icons.calendar_month,
                            title: 'Agendamiento de citas',
                            description: 'Reserva tu cita para atención presencial.',
                          ),
                          SizedBox(height: 12),
                          ServiceCard(
                            icon: Icons.person,
                            title: 'Actualización de datos',
                            description: 'Actualiza tu información personal en el sistema.',
                          ),
                        ],
                      ),
                    ],
                  ),
                ),

                // Pie de página institucional
                Padding(
                  padding: const EdgeInsets.only(top: 12, bottom: 24),
                  child: Column(
                    children: [
                      Divider(thickness: 1, color: Colors.grey[300]),
                      const SizedBox(height: 8),
                      Text(
                        '© 2025 Municipio Digital - Todos los derechos reservados',
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Colors.grey[600]),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Desarrollado por el equipo de Innovación Tecnológica',
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Colors.grey[500]),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
        // Burbuja de chat flotante y movible
        PositionedChatBubble(
          serverIp: widget.serverIp,
        ),
      ],
    );
  }
}

// Widget para la burbuja flotante y movible
class PositionedChatBubble extends StatefulWidget {
  final String serverIp;
  const PositionedChatBubble({Key? key, required this.serverIp}) : super(key: key);

  @override
  State<PositionedChatBubble> createState() => _PositionedChatBubbleState();
}

class _PositionedChatBubbleState extends State<PositionedChatBubble> {
  Offset _offset = const Offset(30, 100);
  bool _showChat = false;

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        if (!_showChat)
          Positioned(
            left: _offset.dx,
            top: _offset.dy,
            child: GestureDetector(
              onPanUpdate: (details) {
                setState(() {
                  _offset += details.delta;
                });
              },
              onTap: () => setState(() => _showChat = true),
              child: Material(
                elevation: 8,
                shape: const CircleBorder(),
                color: Colors.transparent,
                child: CircleAvatar(
                  radius: 32,
                  backgroundColor: AppColors.primary,
                  child: Icon(Icons.smart_toy, color: Colors.white, size: 32),
                ),
              ),
            ),
          ),
        if (_showChat)
          Positioned.fill(
            child: ChatWidget(
              onClose: () => setState(() => _showChat = false),
              serverIp: widget.serverIp,
            ),
          ),
      ],
    );
  }
}


