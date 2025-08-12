import 'dart:convert';
import 'package:flutter/material.dart';
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

class _ChatWidgetState extends State<ChatWidget> {
  final List<ChatMessage> _messages = [];
  final TextEditingController _controller = TextEditingController();
  bool _loading = false;

  @override
  void initState() {
    super.initState();
    _messages.add(ChatMessage(
      text: '¡Hola! Soy el asistente virtual del Municipio. ¿En qué puedo ayudarte hoy?',
      isBot: true,
    ));
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
            Container(
              width: MediaQuery.of(context).size.width,
              height: MediaQuery.of(context).size.height,
              color: Colors.white,
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                        const Padding(
                          padding: EdgeInsets.all(16.0),
                          child: Icon(
                            Icons.android,
                            size: 32,
                            color: Colors.blue,
                          ),
                        ),
                      IconButton(
                        icon: const Icon(Icons.close),
                        onPressed: widget.onClose,
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Expanded(
                    child: ListView.builder(
                      reverse: false,
                      itemCount: _messages.length,
                      itemBuilder: (context, index) {
                        final msg = _messages[index];
                        return Align(
                          alignment: msg.isBot ? Alignment.centerLeft : Alignment.centerRight,
                          child: Container(
                            margin: const EdgeInsets.symmetric(vertical: 4, horizontal: 8),
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                            decoration: BoxDecoration(
                              color: msg.isBot ? Colors.blue[50] : Colors.blue[200],
                              borderRadius: BorderRadius.circular(16),
                            ),
                            child: Text(msg.text),
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
                  const SizedBox(height: 8),
                  Wrap(
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
                  const SizedBox(height: 8),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 8.0),
                    child: Row(
                      children: [
                        Expanded(
                          child: TextField(
                            controller: _controller,
                            onSubmitted: _sendMessage,
                            decoration: const InputDecoration(
                              hintText: 'Escribe tu mensaje...',
                              border: OutlineInputBorder(),
                              isDense: true,
                              contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                            ),
                          ),
                        ),
                        const SizedBox(width: 8),
                        IconButton(
                          icon: const Icon(Icons.send),
                          onPressed: _loading ? null : () => _sendMessage(_controller.text),
                        ),
                      ],
                    ),
                  ),
                ],
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
