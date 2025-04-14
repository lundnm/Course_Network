### Network Analysis and User Interaction with MSI Courses ###
### The program supports master's students at The University of Michigan School of Information
### BY: Lunden Mandigo

### Imports ###
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import json
import time

class Course:
    'A class representing a course.'
    ## create course class and think of attributes/methods
    def __init__(self, id, title, description, prerequisites, terms, credits=None):
        self.credits = credits
        self.id = id
        self.title = title
        self.description = description
        self.prerequisites = prerequisites
        self.terms = terms
    
    def __str__(self):
        return f"{self.id}: {self.title}"

class CourseNetwork:
    'A class representing a network of courses.'

    def __init__(self):
        self.graph = nx.DiGraph()  # Directed graph to represent course prerequisites

    def add_course(self, course):
        self.graph.add_node(course.id, title=course.title, description=course.description, terms=course.terms, credits=course.credits, prerequisites=course.prerequisites)

    def add_prerequisite(self, course_id, prerequisites):
        self.graph.add_edge(u_of_edge=prerequisites, v_of_edge=course_id)

    def load_courses(self, csv_file_path):
        data = pd.read_csv(csv_file_path)  # Load the CSV file into a DataFrame
        data['prerequisites'] = data['prerequisites'].apply(lambda x: json.loads(x) if pd.notna(x) else [])
        # create a node for each course and add it to the graph
        # Iterate through the DataFrame rows and create Course objects
        for _, row in data.iterrows():
            course_id = row['catalog_number']
            title = row['course_title']
            description = row['course_description']
            credits = row['Credits']
            if row['prerequisites'] is not None:
                prerequisites = row['prerequisites']
            else:
                prerequisites = []
            terms = row["typical_term_offered"] if row["typical_term_offered"] else []
                
            course = Course(course_id, title, description, prerequisites, terms, credits)
            self.add_course(course)
                
            
            for prereq in prerequisites:
                self.add_prerequisite(course_id, prereq)

    def visualize(self, filename="my_course_network.png"):
        plt.clf()
        pos = nx.spring_layout(self.graph, k=3)  # positions for all nodes
        nx.draw(self.graph, pos, with_labels=False, node_size=2000, node_color='lightblue', font_size=5, font_weight='bold')
        nx.draw_networkx_labels(self.graph, pos)
        plt.title("Course Network")
        # clear file before saving fig
        
        # save to file
        plt.savefig(filename)
    
    def list_nodes(self):
        'prints a list of all nodes in the graph'
        nodes = [node for node in self.graph.nodes]
        print(nodes)

    def most_central_course(self):
        'Finds the most central course in the network.'
        centrality = nx.betweenness_centrality(self.graph)
        most_central = max(centrality, key=centrality.get)
        print("\n\nBetweenness centrality is a measure of the importance of a node in a network.\n" \
        "It quantifies how often a node acts as a bridge along the shortest path between two other nodes.\n\n")
        time.sleep(2)
        print(f"The most central course in the network is SI {most_central} with a betweenness centrality of {centrality[most_central]}.\n\n")

    def find_shortest_path(self, source, target):
        'Finds the shortest path between two courses in the network.'
        try:
            path = nx.shortest_path(self.graph, source=source, target=target)
            print(f"The shortest path between {source} and {target} is:\n\n")
            print(path)
            return path
        except nx.NetworkXNoPath:
            print(f"No path found between {source} and {target}.")
            print('This may be because the courses are not directly related or there are no prerequisites/corequisites.')
            return None
        except nx.NodeNotFound:
            print(f"One of the courses {source} or {target} does not exist in the graph.")
            return None
        
    def find_prerequisites(self, course):
        'Finds the prerequisites for a course in the network.'
        try:
            prerequisites = list(self.graph.predecessors(course))
            return prerequisites
        except nx.NodeNotFound:
            print(f"The course {course} does not exist in the graph.")
            return None

class Schedule(CourseNetwork):
    'A class representing a schedule of courses.'

    def __init__(self):
        super().__init__()  # Directed graph to represent the schedule
        self.schedule = []
        self.credits = 0
        self.min_credits = 48
        self.track = None

    def add_course(self, course, course_data):
        'Adds a course to the schedule and updates the total credits.'
        self.graph.add_node(course, title=course_data['title'], description=course_data["description"], terms=course_data['terms'], credits=course_data['credits'])
        self.schedule.append(f"{course}: {course_data['title']}")
        try:
            self.credits += float(course_data['credits'])
        except Exception as e:
            print(f"Error: {e}")
            print(f"Invalid credit type for course {course}. Credits must be a number.")
            print(f"The credits for SI {course} are listed as {course_data['credits']} which is type {type(course_data['credits'])}")
            credits = int(input(f"Please enter the number credits for {course} as a number: "))
            self.credits += credits
    
    def view_schedule(self):
        'Displays the current schedule.'
        print("Displaying schedule...")
        time.sleep(1)
        print(f"Current schedule for {self.track}:")
        self.list_nodes()
        print(f"Total credits: {self.credits}")
        print(f'You need to take {self.min_credits - self.credits} more credits to graduate.\n')
        print('You can view your network as a directed graph in the file called "my_course_network.png", which has been saved to the same directory as this program.')

class BDA(Schedule):
    'requirements for a schedule of courses for the BDA program.'
    def __init__(self):
        super().__init__()
        self.track = 'BDA'
        self.requirements = ['500','504', '506', '507', '544', '568', '602', '618', '670', '671']
        self.selectives = ['608', '649', '650', '630']
        self.mastery = ['699.X05']

    def build_schedule(self, graph):
        'Builds the schedule based on the requirements and electives.'
        print("\nBuilding your baseline scedule...")
        time.sleep(2)
        choice = input(f"\nWhich selective requirement would you like to take? {self.selectives}: ")
        for course in self.requirements:
            course_data = graph.graph.nodes[course]
            self.add_course(course, course_data)
            if course_data['prerequisites']:
                for prereq in course_data['prerequisites']:
                    self.add_prerequisite(course, prereq)
        for course in self.selectives:
            if course == choice:
                course_data = graph.graph.nodes[course]
                self.add_course(choice, course_data)
                if course_data['prerequisites']:
                    for prereq in course_data['prerequisites']:
                        self.add_prerequisite(course, prereq)
        course_data = graph.graph.nodes[self.mastery[0]]
        self.add_course(self.mastery[0], course_data)
        if course_data['prerequisites']:
            for prereq in course_data['prerequisites']:
                self.add_prerequisite(self.mastery[0], prereq)
        self.view_schedule()
        self.visualize()
        

class UX(Schedule):
    'requirements for a schedule of courses for the UX program.'
    def __init__(self):
        super().__init__()
        self.track = 'UX'
        self.requirements = ['500', '506', '520', '539', '582', '588', '622']
        self.selectives = ['529', '552', '559', '612', '616', '658', '659', '684']
        self.mastery = ['699.X01']

    def build_schedule(self, graph):
        'Builds the schedule based on the requirements and electives.'
        print("\nBuilding your baseline scedule...")
        time.sleep(2)
        selectives = self.selectives.copy()
        choice1 = input(f"\nWhich selective would you like to take first (select 1)? {selectives}: ")
        selectives.remove(choice1)
        choice2 = input(f"\nWhich selective would you like to take second (select 1)? {selectives}: ")
        choices = [choice1, choice2]
        for course in self.requirements:
            course_data = graph.graph.nodes[course]
            self.add_course(course, course_data)
            if course_data['prerequisites']:
                for prereq in course_data['prerequisites']:
                    self.add_prerequisite(course, prereq)
        for course in self.selectives:
            for c in choices:
                if course == c:
                    course_data = graph.graph.nodes[course]
                    self.add_course(course, course_data)
                    if course_data['prerequisites']:
                        for prereq in course_data['prerequisites']:
                            self.add_prerequisite(course, prereq)
        course_data = graph.graph.nodes[self.mastery[0]]
        self.add_course(self.mastery[0], course_data)
        if course_data['prerequisites']:
            for prereq in course_data['prerequisites']:
                self.add_prerequisite(self.mastery[0], prereq)
        self.view_schedule()
        self.visualize()


def create_user_schedule():
    'Creates a user schedule based on the selected program.'
    print("\nPlease select your program:")
    print("1. BDA")
    print("2. UX")
    print("3. Exit")
    program = input("Enter the number corresponding to your program: ")

    if program == '1':
        return BDA()
    elif program == '2':
        return UX()
    elif program == '3':
        print("Exiting the program...")
        time.sleep(1)
        return exit()
    else:
        print("Invalid selection. Please try again.")
        return create_user_schedule()
    
def first_option(network):
    user_schedule = create_user_schedule()  # Create a user schedule based on the selected program
    user_schedule.build_schedule(network)  # Build the schedule based on the selected program
    choice = input('\nWould you like to see the most central course in your course network? (y/n): ')
    if choice.lower() == 'y':
        user_schedule.most_central_course()

def third_option(network):
    print("Here is a list of all courses in the course network:")
    network.list_nodes()  # List all courses in the course network
    print("Please enter the course IDs of the two courses you want to find the path between.\n")
    course1 = input("Enter the first course ID: ")
    course2 = input("\nEnter the second course ID: ")
    print(f"\nFinding the path between {course1} and {course2}...\n")
    time.sleep(1)
    path = network.find_shortest_path(course1, course2)
    if path:
        print(f"The path between {course1} and {course2} is: {path}\n")

def fourth_option(network):
    print("Here is a list of all courses in the course network:\n")
    network.list_nodes()  # List all courses in the course network
    print("\nPlease enter the course ID of the course you want to find the prerequisites/corequisites for.\n")
    course = input("Enter the course ID: ")
    prerequisites = network.find_prerequisites(course)
    if prerequisites:
        print(f"The prerequisites/corequisites for {course} are: {prerequisites}")
    else:
        print(f"No prerequisites/corequisites found for {course}.\n")

def print_course_info(course, network):
    'Prints the information for a course.'
    course_data = network.graph.nodes[course]
    print(f"\nCourse ID: {course}")
    print(f"Title: {course_data['title']}")
    print(f"Description: {course_data['description']}")
    print(f"Credits: {course_data['credits']}")
    print(f"Terms: {course_data['terms']}")
    print(f"Prerequisites: {course_data['prerequisites']}\n")


    

def main():

    print("\nWelcome to the MSI Course Network!")
    print("This program helps you build a baseline schedule based on your program requirements.")
    print("You can visualize the course network and find the most central course.")
    print("You can also find the path between two courses and the prerequisites/corequisites for a course.\n")
    time.sleep(4)
    while True:
        print("\nPlease select an option:")
        print("1. Build a schedule and visualize the course network")
        print("2. Find the most central course of all UMSI Upper-level courses")
        print("3. Find the shortest path between two courses")
        print("4. Find the prerequisites/corequisites for a course")
        print("5. View course information")
        print("6. Exit\n\n")
        choice = input("Enter the number corresponding to your choice: ")
        if choice == '1':
            first_option(course_network)
        elif choice == '2':
            course_network.most_central_course()  # Find the most central course in the course network
        elif choice == '3':
            third_option(course_network)  # Find the shortest path between two courses
        elif choice == '4':
            fourth_option(course_network)  # Find the prerequisites/corequisites for a course
        elif choice == '5':
            course = input("Enter the course ID: ")
            print_course_info(course, course_network)
        elif choice == '6':
            print("Exiting the program...")
            time.sleep(1)
            exit()
        else:
            print("Invalid selection. Please try again.")


if __name__ == "__main__":
    csv_file_path = 'msi_courses_cleaned.csv'  # the path to your CSV file
    course_network = CourseNetwork()  # Create an instance of CourseNetwork
    course_network.load_courses(csv_file_path)  # Load courses from the CSV file
    # course_network.list_nodes()  # List all courses in the course network
    main()
