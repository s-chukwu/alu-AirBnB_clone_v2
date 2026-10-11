#!/usr/bin/python3
"""
This module contains the entry point of the command interpreter.

"""
import cmd
import re
import shlex
import models
from models.base_model import BaseModel
from models.user import User
from models.state import State
from models.city import City
from models.amenity import Amenity
from models.place import Place
from models.review import Review


class HBNBCommand(cmd.Cmd):
    """
    HBNBCommand class that implements the command interpreter.
    Commands: quit, EOF, help, create, show, destroy, all, update

    """
    prompt = "(hbnb) "
    __classes = {
        "BaseModel": BaseModel,
        "User": User,
        "State": State,
        "City": City,
        "Amenity": Amenity,
        "Place": Place,
        "Review": Review,
    }

    def default(self, line):
        """Handle alternative syntax: <class name>.<command>(<args>)"""
        match = re.match(r"^(\w+)\.(\w+)\((.*)\)$", line)
        if not match:
            return super().default(line)

        cls_name, command, args_str = match.groups()
        if cls_name not in self.__classes:
            print("** class doesn't exist **")
            return

        # Map commands to their standard CLI methods
        command_map = {
            "all": self.do_all,
            "count": self.do_count,
            "show": self.do_show,
            "destroy": self.do_destroy,
            "update": self.do_update
        }

        if command not in command_map:
            return super().default(line)

        # Handle different parameter signatures based on the command
        if command in ["all", "count"]:
            return command_map[command](cls_name)

        # Parse arguments safely for show, destroy, and update
        # Regex extracts individual arguments or full dictionary payloads
        arg_list = re.findall(r'([^, "\[\]{}]+|"[^"]*"|\{.*\})', args_str)
        arg_list = [arg.strip('"') for arg in arg_list]

        if not arg_list:
            return command_map[command](cls_name)

        obj_id = arg_list[0]

        if command in ["show", "destroy"]:
            return command_map[command](f"{cls_name} {obj_id}")

        if command == "update":
            # Check if the second argument is a dictionary string representation
            if len(arg_list) > 1 and arg_list[1].startswith('{') and arg_list[1].endswith('}'):
                dict_str = arg_list[1]
                # Safely convert pseudo-JSON string into an iterable dictionary
                try:
                    import ast
                    attr_dict = ast.literal_eval(dict_str)
                    if isinstance(attr_dict, dict):
                        for key, val in attr_dict.items():
                            self.do_update(f'{cls_name} {obj_id} {key} "{val}"')
                        return
                except (ValueError, SyntaxError):
                    pass

            # Fallback to standard key-value updates
            attr_name = arg_list[1] if len(arg_list) > 1 else ""
            attr_val = arg_list[2] if len(arg_list) > 2 else ""
            return command_map[command](f'{cls_name} {obj_id} {attr_name} "{attr_val}"')

    def do_count(self, arg):
        """
        Retrieve the number of instances of a class.
        Usage: count <class name> or <class name>.count()
        """
        args = shlex.split(arg)
        if not args:
            print("** class name missing **")
            return
        cls_name = args[0]
        if cls_name not in HBNBCommand.__classes:
            print("** class doesn't exist **")
            return

        objs = models.storage.all()
        count = sum(1 for obj in objs.values() if obj.__class__.__name__ == cls_name)
        print(count)

    def do_quit(self, arg):
        """Quit command to exit the program."""
        return True

    def do_EOF(self, arg):
        """EOF signal to exit the program."""
        print("")
        return True

    def emptyline(self):
        """Do nothing on an empty line."""
        pass

    def do_create(self, arg):
        """
        Create a new instance of a class, save it, and print its id.
        Usage: create <class name>
        """
        args = shlex.split(arg)
        if not args:
            print("** class name missing **")
            return
        cls_name = args[0]
        if cls_name not in HBNBCommand.__classes:
            print("** class doesn't exist **")
            return
        obj = HBNBCommand.__classes[cls_name]()
        obj.save()
        print(obj.id)

    def do_show(self, arg):
        """
        Print the string representation of an instance.
        Usage: show <class name> <id>
        """
        args = shlex.split(arg)
        if not args:
            print("** class name missing **")
            return
        cls_name = args[0]
        if cls_name not in HBNBCommand.__classes:
            print("** class doesn't exist **")
            return
        if len(args) < 2:
            print("** instance id missing **")
            return
        key = "{}.{}".format(cls_name, args[1])
        objs = models.storage.all()
        if key not in objs:
            print("** no instance found **")
            return
        print(objs[key])

    def do_destroy(self, arg):
        """
        Delete an instance based on the class name and id.
        Usage: destroy <class name> <id>
        """
        args = shlex.split(arg)
        if not args:
            print("** class name missing **")
            return
        cls_name = args[0]
        if cls_name not in HBNBCommand.__classes:
            print("** class doesn't exist **")
            return
        if len(args) < 2:
            print("** instance id missing **")
            return
        key = "{}.{}".format(cls_name, args[1])
        objs = models.storage.all()
        if key not in objs:
            print("** no instance found **")
            return
        del objs[key]
        models.storage.save()

    def do_all(self, arg):
        """
        Print all string representations of all instances, based or not on the class name.
        Usage: all [class name]
        """
        args = shlex.split(arg)
        objs = models.storage.all()
        result = []
        if args:
            cls_name = args[0]
            if cls_name not in HBNBCommand.__classes:
                print("** class doesn't exist **")
                return
            for key, obj in objs.items():
                if obj.__class__.__name__ == cls_name:
                    result.append(str(obj))
        else:
            for obj in objs.values():
                result.append(str(obj))
        print(result)

    def do_update(self, arg):
        """
        Update an instance based on the class name and id by adding or updating an attribute.
        Usage: update <class name> <id> <attribute name> "<attribute value>"
        """
        args = shlex.split(arg)
        if not args:
            print("** class name missing **")
            return
        cls_name = args[0]
        if cls_name not in HBNBCommand.__classes:
            print("** class doesn't exist **")
            return
        if len(args) < 2:
            print("** instance id missing **")
            return
        key = "{}.{}".format(cls_name, args[1])
        objs = models.storage.all()
        if key not in objs:
            print("** no instance found **")
            return
        if len(args) < 3:
            print("** attribute name missing **")
            return
        if len(args) < 4:
            print("** value missing **")
            return

        attr_name = args[2]
        attr_value = args[3]
        obj = objs[key]

        if hasattr(obj, attr_name):
            current = getattr(obj, attr_name)
            try:
                attr_value = type(current)(attr_value)
            except (ValueError, TypeError):
                pass
        else:
            for cast in (int, float):
                try:
                    attr_value = cast(attr_value)
                    break
                except ValueError:
                    continue

        setattr(obj, attr_name, attr_value)
        obj.save()


if __name__ == "__main__":
    HBNBCommand().cmdloop()
