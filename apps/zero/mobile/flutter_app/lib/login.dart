import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_app/main.dart';

import 'exercise.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({Key? key}) : super(key: key);

  @override
  _LoginPageState createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _globalKey = GlobalKey<FormState>();
  var _username = '';
  var _password = '';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Carved Rock Fitness'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Form(
                key: _globalKey,
                child: Column(
                  children: [
                    TextFormField(
                      decoration: InputDecoration(hintText: 'Username'),
                      onSaved: (newValue) {
                        _username = newValue as String;
                      },
                    ),
                    TextFormField(
                        decoration: InputDecoration(hintText: 'Password'),
                        onSaved: (newValue) {
                          _password = newValue as String;
                        }),
                  ],
                )),
            ElevatedButton(
              onPressed: () async {
                _globalKey.currentState!.save();
                var credentials = '$_username:$_password';
                var bytes = utf8.encode(credentials);
                var b64 = base64.encode(bytes);

                var httpClient = HttpClient();
                var request =
                    await httpClient.get('10.0.2.2', 5000, '/program');
                request.headers
                    .add(HttpHeaders.authorizationHeader, 'Basic $b64');

                var response = await request.close();

                var stringBuffer = StringBuffer();

                if (response.statusCode == 401 || response.statusCode == 403) {
                  showDialog(
                      context: context,
                      builder: (_) {
                        return AlertDialog(
                            content: Text('Unauthorized or not allowed'),
                            title: Text('Error'),
                            actions: [
                              TextButton(
                                child: Text('OK'),
                                onPressed: () {
                                  Navigator.of(context).pop();
                                },
                              )
                            ]);
                      });
                } else {
                  response.transform(utf8.decoder).listen((chunk) {
                    stringBuffer.write(chunk);
                  }, onDone: () {
                    // var exercises = jsonDecode(stringBuffer.toString()) as List;
                    // exercises = exercises
                    //     .map((exercise) => Exercise.fromJson(exercise))
                    //     .toList();

                    Navigator.push(context,
                        MaterialPageRoute(builder: (_) => const MyHomePage()));
                  });
                }
              },
              child: Text('Login'),
            ),
          ],
        ),
      ),
    );
  }
}
