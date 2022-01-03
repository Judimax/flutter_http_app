import 'package:json_annotation/json_annotation.dart';

part 'exercise.g.dart';

@JsonSerializable(fieldRename: FieldRename.snake)
class Exercise {
  String title;
  int reps;

  Exercise(this.title, this.reps);

  factory Exercise.fromJson(Map<String, dynamic> exerciseMap) {
    return _$ExerciseFromJson(exerciseMap);
  }
}
