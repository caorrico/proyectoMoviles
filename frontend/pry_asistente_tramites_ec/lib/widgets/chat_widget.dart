import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/animation.dart';
import 'package:http/http.dart' as http;

import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'quick_questions.dart';





class ChatWidget extends StatefulWidget {
  final VoidCallback onClose;
  final String serverIp;
  const ChatWidget({Key? key, required this.onClose, required this.serverIp}) : super(key: key);

  @override
  State<ChatWidget> createState() => _ChatWidgetState();
}

class _ChatWidgetState extends State<ChatWidget> with SingleTickerProviderStateMixin {
  final List<ChatMessage> _messages = [];
  final TextEditingController _controller = TextEditingController();
  bool _loading = false;
  late AnimationController _animController;
  late Animation<double> _scaleAnim;

  @override
  void initState() {
    super.initState();
    _messages.add(ChatMessage(
      text: '¡Hola! Soy el asistente virtual del Municipio. ¿En qué puedo ayudarte hoy?',
      isBot: true,
    ));
    _animController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 350),
    );
    _scaleAnim = CurvedAnimation(parent: _animController, curve: Curves.easeOutBack);
    _animController.forward();
  }

  @override
  void dispose() {
    _animController.dispose();
    super.dispose();
  }

  Future<void> _sendMessage(String text) async {
    if (text.trim().isEmpty) return;
    setState(() {
      _messages.add(ChatMessage(text: text, isBot: false));
      _loading = true;
    });
    _controller.clear();
    try {
      final url = Uri.parse('http://${widget.serverIp}:8000/chat');
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'query_text': text}),
      ).timeout(const Duration(seconds: 60));
      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(utf8.decode(response.bodyBytes));
        setState(() {
          _messages.add(ChatMessage(text: jsonResponse['response'], isBot: true));
        });
      } else {
        setState(() {
          _messages.add(ChatMessage(text: 'Lo siento, no pude conectarme con mis servicios. Intenta más tarde.', isBot: true));
        });
      }
    } catch (_) {
      setState(() {
        _messages.add(ChatMessage(text: 'Error de conexión. Intenta más tarde.', isBot: true));
      });
    } finally {
      setState(() {
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.black.withOpacity(0.3),
      child: SafeArea(
        child: Stack(
          children: [
            Center(
              child: ScaleTransition(
                scale: _scaleAnim,
                child: Container(
                  width: MediaQuery.of(context).size.width > 500 ? 400 : MediaQuery.of(context).size.width * 0.98,
                  height: MediaQuery.of(context).size.height * 0.80,
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(28),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.18),
                        blurRadius: 32,
                        offset: const Offset(0, 8),
                      ),
                    ],
                    border: Border.all(color: Colors.blue[100]!, width: 1.2),
                  ),
                  child: Column(
                    children: [
                      // Header con logo y botón cerrar
                      Container(
                        decoration: const BoxDecoration(
                          color: Color(0xFF005fa3),
                          borderRadius: BorderRadius.only(
                            topLeft: Radius.circular(28),
                            topRight: Radius.circular(28),
                          ),
                        ),
                        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Row(
                              children: [
                                CircleAvatar(
                                  backgroundColor: Colors.white,
                                  radius: 18,
                                  child: Icon(Icons.smart_toy, color: Color(0xFF005fa3), size: 22),
                                ),
                                const SizedBox(width: 10),
                                const Text(
                                  'Asistente',
                                  style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 18),
                                ),
                              ],
                            ),
                            IconButton(
                              icon: const Icon(Icons.close, color: Colors.white),
                              onPressed: () {
                                _animController.reverse().then((_) => widget.onClose());
                              },
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 4),
                      // Mensajes
                      Expanded(
                        child: ListView.builder(
                          reverse: false,
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
                          itemCount: _messages.length,
                          itemBuilder: (context, index) {
                            final msg = _messages[index];
                            final isBot = msg.isBot;
                            return AnimatedContainer(
                              duration: const Duration(milliseconds: 320),
                              curve: Curves.easeOut,
                              child: Row(
                                mainAxisAlignment: isBot ? MainAxisAlignment.start : MainAxisAlignment.end,
                                crossAxisAlignment: CrossAxisAlignment.end,
                                children: [
                                  if (isBot)
                                    Padding(
                                      padding: const EdgeInsets.only(right: 4, bottom: 2),
                                      child: CircleAvatar(
                                        backgroundColor: Colors.blue[100],
                                        radius: 16,
                                        child: Icon(Icons.smart_toy, color: Color(0xFF005fa3), size: 18),
                                      ),
                                    ),
                                  Flexible(
                                    child: Container(
                                      margin: EdgeInsets.only(
                                        left: isBot ? 0 : 40,
                                        right: isBot ? 40 : 0,
                                        top: 4,
                                        bottom: 4,
                                      ),
                                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                                      decoration: BoxDecoration(
                                        color: isBot ? Colors.blue[50] : Colors.blue[200],
                                        borderRadius: BorderRadius.only(
                                          topLeft: const Radius.circular(18),
                                          topRight: const Radius.circular(18),
                                          bottomLeft: Radius.circular(isBot ? 4 : 18),
                                          bottomRight: Radius.circular(isBot ? 18 : 4),
                                        ),
                                        boxShadow: [
                                          BoxShadow(
                                            color: Colors.blue.withOpacity(0.07),
                                            blurRadius: 4,
                                            offset: const Offset(0, 2),
                                          ),
                                        ],
                                      ),
                                      child: Text(
                                        msg.text,
                                        style: TextStyle(
                                          color: isBot ? Color(0xFF005fa3) : Colors.white,
                                          fontSize: 15,
                                        ),
                                      ),
                                    ),
                                  ),
                                  if (!isBot)
                                    Padding(
                                      padding: const EdgeInsets.only(left: 4, bottom: 2),
                                      child: CircleAvatar(
                                        backgroundColor: Colors.blue[200],
                                        radius: 16,
                                        child: Icon(Icons.person, color: Colors.white, size: 18),
                                      ),
                                    ),
                                ],
                              ),
                            );
                          },
                        ),
                      ),
                      if (_loading)
                        const Padding(
                          padding: EdgeInsets.symmetric(vertical: 8),
                          child: CircularProgressIndicator(strokeWidth: 2),
                        ),
                      const SizedBox(height: 4),
                      // Preguntas rápidas
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 8.0),
                        child: Wrap(
                          spacing: 8,
                          children: [
                            ...[
                              '¿Cuáles son los requisitos para obtener una cédula?',
                              '¿Dónde puedo pagar mis impuestos?',
                              '¿Cómo agendo una cita?',
                            ].map((q) => ActionChip(
                                  label: Text(q),
                                  onPressed: () => _sendMessage(q),
                                )),
                          ],
                        ),
                      ),
                      const SizedBox(height: 4),
                      // Input
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 8.0),
                        child: Row(
                          children: [
                            Expanded(
                              child: TextField(
                                controller: _controller,
                                onSubmitted: _sendMessage,
                                decoration: InputDecoration(
                                  hintText: 'Escribe tu mensaje...'
                                      ,
                                  border: OutlineInputBorder(
                                    borderRadius: BorderRadius.circular(18),
                                    borderSide: BorderSide(color: Colors.blue[100]!),
                                  ),
                                  isDense: true,
                                  contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                                ),
                              ),
                            ),
                            const SizedBox(width: 8),
                            Container(
                              decoration: BoxDecoration(
                                color: _loading ? Colors.grey : Color(0xFF005fa3),
                                borderRadius: BorderRadius.circular(18),
                              ),
                              child: IconButton(
                                icon: const Icon(Icons.send, color: Colors.white),
                                onPressed: _loading ? null : () => _sendMessage(_controller.text),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class ChatMessage {
  final String text;
  final bool isBot;
  ChatMessage({required this.text, required this.isBot});
}
