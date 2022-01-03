// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'userprofile.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

UserProfile _$UserProfileFromJson(Map<String, dynamic> json) => UserProfile(
      firstName: json['first_name'],
      lastName: json['last_name'],
      isActive: json['is_active'],
      loyaltyPoints: json['loyalty_points'],
      fitnessGoal: json['fitness_goal'],
    );

Map<String, dynamic> _$UserProfileToJson(UserProfile instance) =>
    <String, dynamic>{
      'first_name': instance.firstName,
      'last_name': instance.lastName,
      'loyalty_points': instance.loyaltyPoints,
      'fitness_goal': instance.fitnessGoal,
      'is_active': instance.isActive,
    };
