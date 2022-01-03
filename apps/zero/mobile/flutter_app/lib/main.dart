import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_app/userprofile.dart';
import 'package:http/http.dart' as http;

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Demo',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: const MyHomePage(title: 'Flutter Demo Home Page'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({Key? key, required this.title}) : super(key: key);

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  final _globalKey = GlobalKey<FormState>();
  var userProfile = UserProfile();
  var profiles = [];

  @override
  void initState() {
    super.initState();
  }

  Future<bool> _loadProfiles() async {
    var response = await http.get(Uri.parse('http://10.0.2.2:5000/profile'));
    profiles = jsonDecode(response.body) as List;
    profiles = profiles.map((profile) {
      return UserProfile.fromJson(profile);
    }).toList();
    return true;
  }

  @override
  Widget build(BuildContext context) {
    double width = MediaQuery.of(context).size.width;
    double height = MediaQuery.of(context).size.height;
    return SizedBox(
      height: height / 2,
      width: width,
      child: FutureBuilder(
        future: _loadProfiles(),
        builder: (context, snapshot) {
          if (snapshot.hasData) {
            return Scaffold(
              appBar: AppBar(
                title: Text(widget.title),
              ),
              body: ListView(
                children: <Widget>[
                  Form(
                    key: _globalKey,
                    child: Column(children: [
                      TextFormField(
                        decoration:
                            const InputDecoration(hintText: 'First Name'),
                        validator: (currentValue) {
                          if (currentValue!.isEmpty) {
                            return 'First name is required';
                          }
                        },
                        onSaved: (currentValue) {
                          userProfile.firstName = currentValue;
                        },
                      ),
                      TextFormField(
                        decoration:
                            const InputDecoration(hintText: 'Last Name'),
                        validator: (currentValue) {
                          if (currentValue!.isEmpty) {
                            return 'Last name is required';
                          }
                        },
                        onSaved: (currentValue) {
                          userProfile.lastName = currentValue;
                        },
                      ),
                      TextFormField(
                        decoration:
                            const InputDecoration(hintText: 'Loyalty Points'),
                        keyboardType: TextInputType.number,
                        validator: (currentValue) {
                          if (int.parse(currentValue!) <= 0) {
                            return 'Loyalty point must be greater than zero';
                          }
                        },
                        onSaved: (currentValue) {
                          userProfile.loyaltyPoints = int.parse(currentValue!);
                        },
                      ),
                      DropdownButtonFormField(
                        decoration:
                            const InputDecoration(hintText: 'Fitness Goal'),
                        onChanged: (newValue) {},
                        items: [
                          ['Lose weight', 1],
                          ['Build muscle', 2],
                          ['Train for a sport', 3],
                          ['Recreation', 4]
                        ].map((item) {
                          return DropdownMenuItem(
                              child: Text(item[0] as String), value: item[1]);
                        }).toList(),
                        onSaved: (currentValue) {
                          userProfile.fitnessGoal = currentValue as int;
                        },
                      ),
                      SwitchListTile(
                        value: userProfile.isActive as bool,
                        onChanged: (newValue) {
                          setState(() {
                            userProfile.isActive = newValue;
                          });
                        },
                        title: Text('Active'),
                      ),
                      ElevatedButton(
                          child: Text('Submit'),
                          onPressed: () async {
                            var _message = '';
                            if (_globalKey.currentState!.validate()) {
                              _globalKey.currentState!.save();
                              _message = userProfile.toJson();
                            } else {
                              _message = 'There was an error in the form';
                            }
                            late var body;
                            late var statusCode;
                            var stringBuffer = StringBuffer();
                            late HttpClientResponse response;
                            try {
                              // doesnt work because content-type cant be overriden>
                              // var response = await http.post(
                              //     Uri.parse('https://10.0.2.2:5000/profile'),
                              //     body: userProfile.toJson(),
                              //     headers: {'Content-type': 'application/json'});
                              // body = response.body;
                              // statusCode = response.statusCode;
                              var httpClient = HttpClient();
                              var request = await httpClient.post(
                                  '10.0.2.2', 5000, '/profile');
                              request.headers.contentType = ContentType.json;
                              request.write(_message);
                              response = await request.close();
                              response.transform(utf8.decoder).listen((chunk) {
                                stringBuffer.write(chunk);
                              });
                            } catch (e) {
                              print(e);
                              // return;
                            }

                            showDialog(
                                context: context,
                                builder: (_) {
                                  return AlertDialog(
                                    title: Text('Generated JSON'),
                                    content: Text(
                                        '${stringBuffer.toString()}, ${response.statusCode}'),
                                    // content: Text('$body, $statusCode'),
                                    // content: Text(_message),
                                    actions: [
                                      TextButton(
                                        child: Text('OK'),
                                        onPressed: () {
                                          Navigator.of(context).pop();
                                        },
                                      ),
                                    ],
                                  );
                                });
                          })
                    ]),
                  ),
                  ListView.builder(
                    shrinkWrap: true,
                    physics: const ScrollPhysics(),
                    itemCount: profiles.length,
                    itemBuilder: (context, index) {
                      return ListTile(
                          title: Text(
                              '${profiles[index].firstName} ${profiles[index].lastName}'),
                          onTap: () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (_) =>
                                    ProfileDetail(item: profiles[index]),
                              ),
                            );
                          });
                    },
                  )
                ],
              ),
            );
          } else {
            return const Text('Loading ...');
          }
        },
      ),
    );
  }
}

class ProfileDetail extends StatelessWidget {
  final UserProfile item;

  final fitnessGoals = [
    '',
    'Lose weight',
    'Build muscle',
    'Train for a sport',
    'Recreation'
  ];

  ProfileDetail({Key? key, required this.item}) : super(key: key);

  String _getFitnessGoal(int fitnessGoal) {
    return fitnessGoals[fitnessGoal];
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Profile details'),
      ),
      body: Table(
        children: [
          TableRow(children: [
            Text('First Name', style: TextStyle(fontWeight: FontWeight.bold)),
            Text(item.firstName as String),
          ]),
          TableRow(children: [
            Text('Last Name', style: TextStyle(fontWeight: FontWeight.bold)),
            Text(item.lastName as String),
          ]),
          TableRow(children: [
            Text('Is Active', style: TextStyle(fontWeight: FontWeight.bold)),
            Text(item.isActive as bool ? 'Yes' : 'No'),
          ]),
          TableRow(children: [
            Text('Loyalty Points',
                style: TextStyle(fontWeight: FontWeight.bold)),
            Text(item.loyaltyPoints.toString()),
          ]),
          TableRow(children: [
            Text('Fitness Goal', style: TextStyle(fontWeight: FontWeight.bold)),
            Text(_getFitnessGoal(item.fitnessGoal as int)),
          ]),
        ],
      ),
    );
  }
}
