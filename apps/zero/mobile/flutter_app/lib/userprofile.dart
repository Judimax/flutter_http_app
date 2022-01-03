import 'dart:convert';

import 'package:json_annotation/json_annotation.dart';

part 'userprofile.g.dart';

@JsonSerializable(fieldRename: FieldRename.snake)
class UserProfile {
  // @JsonKey(ignore: true)
  String? firstName;
  String? lastName;
  int? loyaltyPoints;
  int? fitnessGoal;
  bool? isActive;

  UserProfile({firstName , lastName, isActive, loyaltyPoints, fitnessGoal}) {
    this.firstName = firstName;
    this.lastName = lastName;
    this.isActive = isActive ?? false;
    this.loyaltyPoints = loyaltyPoints;
    this.fitnessGoal = fitnessGoal;
  }

  factory UserProfile.fromJson(Map<String, dynamic> userMap) {
    // return UserProfile(
    //   userMap['first_name'],
    //   userMap['last_name'],
    //   userMap['is_active'],
    //   userMap['loyalty_points'],
    //   userMap['fitness_goal'],
    // );
    return _$UserProfileFromJson(userMap);
  }

  String toJson() {
    Map<String, dynamic> userMap = _$UserProfileToJson(this);
    var userJson = json.encode(userMap);
    return userJson;
  }
}
