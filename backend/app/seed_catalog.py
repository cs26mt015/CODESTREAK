"""Additional deterministic practice problems used by the local demo seed."""


def _problem(title, difficulty, statement, sample_input, sample_output, solution, cases, tags):
    return {
        "title": title,
        "difficulty": difficulty,
        "statement": statement,
        "constraints": "Input follows the format in the statement; integer values fit in signed 64-bit range.",
        "sample_input": sample_input,
        "sample_output": sample_output,
        "editorial_notes": "Read the input in order, apply the stated operation, and print the result.",
        "reference_solution": solution.strip(),
        "hidden_test_cases": [{"input": item, "output": result} for item, result in cases],
        "tags": tags,
    }


ADDITIONAL_PROBLEMS = (
    _problem("Find the Smallest Number", "Easy", "Read n followed by n integers and print the smallest integer.", "4\n8 -3 5 2", "-3", r"""
#include <iostream>
int main(){int n; long long x,b; std::cin>>n>>b; for(int i=1;i<n;i++){std::cin>>x;if(x<b)b=x;} std::cout<<b<<std::endl;}
""", [("4\n8 -3 5 2\n", "-3\n"), ("1\n9\n", "9\n"), ("3\n-8 -2 -5\n", "-8\n")], ["Arrays", "Minimum"]),
    _problem("Count Even Numbers", "Easy", "Read n followed by n integers. Print how many of them are even.", "6\n1 2 3 4 6 9", "3", r"""
#include <iostream>
int main(){int n,c=0; long long x; std::cin>>n; while(n--){std::cin>>x;if(x%2==0)c++;} std::cout<<c<<std::endl;}
""", [("6\n1 2 3 4 6 9\n", "3\n"), ("3\n-2 -1 0\n", "2\n"), ("2\n1 3\n", "0\n")], ["Arrays", "Counting"]),
    _problem("Sum Odd Numbers", "Easy", "Read n followed by n integers and print the sum of the odd values.", "5\n1 2 3 4 5", "9", r"""
#include <iostream>
int main(){int n; long long x,s=0; std::cin>>n; while(n--){std::cin>>x;if(x%2!=0)s+=x;} std::cout<<s<<std::endl;}
""", [("5\n1 2 3 4 5\n", "9\n"), ("3\n-3 2 -1\n", "-4\n"), ("2\n4 8\n", "0\n")], ["Arrays", "Arithmetic"]),
    _problem("Factorial", "Easy", "Read n (0 <= n <= 20) and print n factorial. Define 0! as 1.", "5", "120", r"""
#include <iostream>
int main(){int n; long long x=1; std::cin>>n; for(int i=2;i<=n;i++)x*=i; std::cout<<x<<std::endl;}
""", [("5\n", "120\n"), ("0\n", "1\n"), ("10\n", "3628800\n")], ["Math", "Loops"]),
    _problem("Nth Fibonacci Number", "Easy", "Read n (0 <= n <= 92) and print F(n), where F(0)=0, F(1)=1, and F(n)=F(n-1)+F(n-2).", "7", "13", r"""
#include <iostream>
int main(){int n; long long a=0,b=1; std::cin>>n; for(int i=0;i<n;i++){long long c=a+b;a=b;if(i+1<n)b=c;} std::cout<<a<<std::endl;}
""", [("7\n", "13\n"), ("0\n", "0\n"), ("10\n", "55\n")], ["Math", "Dynamic Programming"]),
    _problem("Prime Number Check", "Easy", "Read an integer n and print YES if n is prime, otherwise print NO. Values below 2 are not prime.", "29", "YES", r"""
#include <iostream>
int main(){long long n;std::cin>>n;bool p=n>=2;for(long long d=2;d*d<=n&&p;d++)if(n%d==0)p=false;std::cout<<(p?"YES":"NO")<<std::endl;}
""", [("29\n", "YES\n"), ("1\n", "NO\n"), ("49\n", "NO\n")], ["Math", "Number Theory"]),
    _problem("Count Primes up to N", "Easy", "Read n and print the number of prime integers in the inclusive range [2, n].", "10", "4", r"""
#include <iostream>
int main(){int n,c=0;std::cin>>n;for(int x=2;x<=n;x++){bool p=true;for(int d=2;d*d<=x;d++)if(x%d==0){p=false;break;}if(p)c++;}std::cout<<c<<std::endl;}
""", [("10\n", "4\n"), ("1\n", "0\n"), ("20\n", "8\n")], ["Math", "Number Theory"]),
    _problem("Greatest Common Divisor", "Easy", "Read two non-negative integers a and b and print their greatest common divisor. gcd(0, 0) is 0.", "48 18", "6", r"""
#include <iostream>
int main(){long long a,b;std::cin>>a>>b;while(b){long long t=a%b;a=b;b=t;}std::cout<<a<<std::endl;}
""", [("48 18\n", "6\n"), ("0 9\n", "9\n"), ("0 0\n", "0\n")], ["Math", "Number Theory"]),
    _problem("Least Common Multiple", "Easy", "Read two positive integers a and b and print their least common multiple.", "12 18", "36", r"""
#include <iostream>
long long gcd(long long a,long long b){while(b){long long t=a%b;a=b;b=t;}return a;}
int main(){long long a,b;std::cin>>a>>b;std::cout<<a/gcd(a,b)*b<<std::endl;}
""", [("12 18\n", "36\n"), ("7 5\n", "35\n"), ("21 6\n", "42\n")], ["Math", "Number Theory"]),
    _problem("Reverse an Integer", "Easy", "Read a non-negative integer and print its digits in reverse order. Leading zeroes in the reversed result are omitted.", "12040", "4021", r"""
#include <iostream>
int main(){long long n,r=0;std::cin>>n;do{r=r*10+n%10;n/=10;}while(n);std::cout<<r<<std::endl;}
""", [("12040\n", "4021\n"), ("7\n", "7\n"), ("1000\n", "1\n")], ["Math", "Digits"]),
    _problem("Integer Palindrome Check", "Easy", "Read a non-negative integer and print YES if its decimal representation reads the same forward and backward; otherwise print NO.", "12321", "YES", r"""
#include <iostream>
int main(){long long n;std::cin>>n;long long x=n,r=0;do{r=r*10+x%10;x/=10;}while(x);std::cout<<(r==n?"YES":"NO")<<std::endl;}
""", [("12321\n", "YES\n"), ("120\n", "NO\n"), ("0\n", "YES\n")], ["Math", "Digits"]),
    _problem("Sum of Digits", "Easy", "Read a non-negative integer and print the sum of its decimal digits.", "5082", "15", r"""
#include <iostream>
int main(){long long n,s=0;std::cin>>n;while(n){s+=n%10;n/=10;}std::cout<<s<<std::endl;}
""", [("5082\n", "15\n"), ("0\n", "0\n"), ("999\n", "27\n")], ["Math", "Digits"]),
    _problem("Count Digits", "Easy", "Read a non-negative integer and print the number of digits in its usual decimal representation. Zero has one digit.", "10005", "5", r"""
#include <iostream>
int main(){long long n;std::cin>>n;int c=0;do{c++;n/=10;}while(n);std::cout<<c<<std::endl;}
""", [("10005\n", "5\n"), ("0\n", "1\n"), ("8\n", "1\n")], ["Math", "Digits"]),
    _problem("Integer Power", "Easy", "Read integers a and b, where 0 <= b <= 30, and print a raised to the power b. Inputs are chosen so the result fits in signed 64-bit range.", "3 4", "81", r"""
#include <iostream>
int main(){long long a,r=1;int b;std::cin>>a>>b;while(b--)r*=a;std::cout<<r<<std::endl;}
""", [("3 4\n", "81\n"), ("9 0\n", "1\n"), ("-2 5\n", "-32\n")], ["Math", "Exponentiation"]),
    _problem("Leap Year", "Easy", "Read a year and print YES if it is a leap year in the Gregorian calendar, otherwise print NO.", "2000", "YES", r"""
#include <iostream>
int main(){int y;std::cin>>y;std::cout<<((y%400==0||(y%4==0&&y%100!=0))?"YES":"NO")<<std::endl;}
""", [("2000\n", "YES\n"), ("1900\n", "NO\n"), ("2024\n", "YES\n")], ["Conditionals", "Dates"]),
    _problem("Second Largest Distinct Value", "Medium", "Read n (n >= 2) and n integers. Print the second-largest distinct value. The input always contains at least two distinct values.", "6\n4 9 2 9 7 1", "7", r"""
#include <iostream>
#include <climits>
int main(){int n;std::cin>>n;long long a=LLONG_MIN,b=LLONG_MIN,x;while(n--){std::cin>>x;if(x>a){b=a;a=x;}else if(x<a&&x>b)b=x;}std::cout<<b<<std::endl;}
""", [("6\n4 9 2 9 7 1\n", "7\n"), ("3\n-5 -2 -9\n", "-5\n"), ("4\n8 8 3 3\n", "3\n")], ["Arrays", "Sorting"]),
    _problem("Linear Search", "Easy", "Read n, n integers, and a target x. Print the zero-based index of its first occurrence, or -1 if it is absent.", "5\n4 8 2 8 1\n8", "1", r"""
#include <iostream>
int main(){int n;long long x,v;std::cin>>n;long long a[200000];for(int i=0;i<n;i++)std::cin>>a[i];std::cin>>x;int ans=-1;for(int i=0;i<n;i++)if(a[i]==x){ans=i;break;}std::cout<<ans<<std::endl;}
""", [("5\n4 8 2 8 1\n8\n", "1\n"), ("3\n1 2 3\n4\n", "-1\n"), ("1\n-7\n-7\n", "0\n")], ["Arrays", "Searching"]),
    _problem("Binary Search", "Easy", "Read n, n integers in non-decreasing order, and a target x. Print the zero-based index of its first occurrence, or -1 if absent.", "6\n1 3 3 5 8 9\n3", "1", r"""
#include <iostream>
int main(){int n;std::cin>>n;long long a[200000],x;for(int i=0;i<n;i++)std::cin>>a[i];std::cin>>x;int l=0,r=n-1,ans=-1;while(l<=r){int m=l+(r-l)/2;if(a[m]>=x)r=m-1;else l=m+1;}if(l<n&&a[l]==x)ans=l;std::cout<<ans<<std::endl;}
""", [("6\n1 3 3 5 8 9\n3\n", "1\n"), ("4\n2 4 6 8\n7\n", "-1\n"), ("1\n5\n5\n", "0\n")], ["Arrays", "Binary Search"]),
    _problem("Reverse an Array", "Easy", "Read n followed by n integers and print them in reverse order, separated by single spaces.", "5\n1 2 3 4 5", "5 4 3 2 1", r"""
#include <iostream>
int main(){int n;std::cin>>n;long long a[200000];for(int i=0;i<n;i++)std::cin>>a[i];for(int i=n-1;i>=0;i--)std::cout<<a[i]<<(i?" ":"");std::cout<<std::endl;}
""", [("5\n1 2 3 4 5\n", "5 4 3 2 1\n"), ("1\n42\n", "42\n"), ("3\n-1 0 8\n", "8 0 -1\n")], ["Arrays", "Reversal"]),
    _problem("Rotate Array Right", "Medium", "Read n, k, and n integers. Rotate the array right by k positions (k may exceed n) and print the result separated by spaces.", "5 2\n1 2 3 4 5", "4 5 1 2 3", r"""
#include <iostream>
int main(){int n;long long k;std::cin>>n>>k;long long a[200000];for(int i=0;i<n;i++)std::cin>>a[i];k%=n;for(int i=0;i<n;i++)std::cout<<a[(i+n-k)%n]<<(i+1<n?" ":"");std::cout<<std::endl;}
""", [("5 2\n1 2 3 4 5\n", "4 5 1 2 3\n"), ("4 6\n1 2 3 4\n", "3 4 1 2\n"), ("1 99\n7\n", "7\n")], ["Arrays", "Rotation"]),
    _problem("Remove Duplicates from Sorted Array", "Easy", "Read n integers in non-decreasing order. Print each distinct value once, preserving order, separated by spaces.", "7\n1 1 2 2 2 4 5", "1 2 4 5", r"""
#include <iostream>
int main(){int n;std::cin>>n;long long x,last=0;bool first=true;for(int i=0;i<n;i++){std::cin>>x;if(first||x!=last){if(!first)std::cout<<" ";std::cout<<x;first=false;last=x;}}std::cout<<std::endl;}
""", [("7\n1 1 2 2 2 4 5\n", "1 2 4 5\n"), ("3\n-1 -1 -1\n", "-1\n"), ("4\n1 2 3 4\n", "1 2 3 4\n")], ["Arrays", "Two Pointers"]),
    _problem("Array Sum", "Easy", "Read n followed by n integers and print their sum.", "5\n2 -1 3 4 2", "10", r"""
#include <iostream>
int main(){int n;long long x,s=0;std::cin>>n;while(n--){std::cin>>x;s+=x;}std::cout<<s<<std::endl;}
""", [("5\n2 -1 3 4 2\n", "10\n"), ("1\n-9\n", "-9\n"), ("4\n0 0 0 0\n", "0\n")], ["Arrays", "Arithmetic"]),
    _problem("Missing Number from 0 to N", "Easy", "Read n and then n distinct integers from [0, n]. Exactly one value is missing. Print the missing value.", "4\n3 0 1 4", "2", r"""
#include <iostream>
int main(){long long n,x,s=0;std::cin>>n;for(long long i=0;i<n;i++){std::cin>>x;s+=x;}std::cout<<n*(n+1)/2-s<<std::endl;}
""", [("4\n3 0 1 4\n", "2\n"), ("1\n0\n", "1\n"), ("3\n1 2 3\n", "0\n")], ["Arrays", "Math"]),
    _problem("Merge Two Sorted Arrays", "Easy", "Read n, m, then two non-decreasing arrays of those lengths. Print all values in non-decreasing order, separated by spaces.", "3 4\n1 4 8\n2 3 9 10", "1 2 3 4 8 9 10", r"""
#include <iostream>
int main(){int n,m;std::cin>>n>>m;long long a[200000],b[200000];for(int i=0;i<n;i++)std::cin>>a[i];for(int i=0;i<m;i++)std::cin>>b[i];int i=0,j=0;bool first=true;while(i<n||j<m){long long x;if(j==m||(i<n&&a[i]<=b[j]))x=a[i++];else x=b[j++];if(!first)std::cout<<" ";std::cout<<x;first=false;}std::cout<<std::endl;}
""", [("3 4\n1 4 8\n2 3 9 10\n", "1 2 3 4 8 9 10\n"), ("1 2\n5\n1 7\n", "1 5 7\n"), ("2 1\n-3 0\n-1\n", "-3 -1 0\n")], ["Arrays", "Two Pointers"]),
    _problem("Range Sum Queries", "Easy", "Read n, an array of n integers, then q queries. Each query contains 1-based l and r. Print the sum of values from l through r for every query.", "5\n2 4 1 3 5\n3\n1 3\n2 5\n4 4", "7\n13\n3", r"""
#include <iostream>
int main(){int n;std::cin>>n;long long p[200001]={0},x;for(int i=1;i<=n;i++){std::cin>>x;p[i]=p[i-1]+x;}int q,l,r;std::cin>>q;while(q--){std::cin>>l>>r;std::cout<<p[r]-p[l-1]<<std::endl;}}
""", [("5\n2 4 1 3 5\n3\n1 3\n2 5\n4 4\n", "7\n13\n3\n"), ("3\n-1 5 2\n2\n1 1\n1 3\n", "-1\n6\n"), ("1\n9\n1\n1 1\n", "9\n")], ["Arrays", "Prefix Sum"]),
    _problem("Pair with Target Sum", "Easy", "Read n, n integers, and target t. Print YES if two different array elements sum to t; otherwise print NO.", "5\n2 7 11 15 1\n9", "YES", r"""
#include <iostream>
#include <unordered_set>
int main(){int n;long long x,t;std::cin>>n;std::unordered_set<long long>s;bool ok=false;long long a[200000];for(int i=0;i<n;i++)std::cin>>a[i];std::cin>>t;for(int i=0;i<n;i++){if(s.count(t-a[i]))ok=true;s.insert(a[i]);}std::cout<<(ok?"YES":"NO")<<std::endl;}
""", [("5\n2 7 11 15 1\n9\n", "YES\n"), ("3\n1 2 4\n8\n", "NO\n"), ("4\n-2 5 7 0\n5\n", "YES\n")], ["Arrays", "Hashing"]),
    _problem("Two Sum Indices", "Easy", "Read n, n integers, and target t. Print the zero-based indices of the first pair i < j whose values sum to t. It is guaranteed a pair exists.", "4\n2 7 11 15\n9", "0 1", r"""
#include <iostream>
#include <unordered_map>
int main(){int n;long long x,t;std::cin>>n;long long a[200000];for(int i=0;i<n;i++)std::cin>>a[i];std::cin>>t;std::unordered_map<long long,int>m;for(int j=0;j<n;j++){auto it=m.find(t-a[j]);if(it!=m.end()){std::cout<<it->second<<" "<<j<<std::endl;return 0;}if(!m.count(a[j]))m[a[j]]=j;}}
""", [("4\n2 7 11 15\n9\n", "0 1\n"), ("4\n3 2 4 3\n6\n", "1 2\n"), ("2\n-1 5\n4\n", "0 1\n")], ["Arrays", "Hashing"]),
    _problem("Bubble Sort", "Easy", "Read n followed by n integers. Sort them in non-decreasing order and print them separated by spaces.", "5\n5 1 4 2 8", "1 2 4 5 8", r"""
#include <iostream>
int main(){int n;std::cin>>n;long long a[200000];for(int i=0;i<n;i++)std::cin>>a[i];for(int i=0;i<n;i++)for(int j=0;j+1<n-i;j++)if(a[j]>a[j+1])std::swap(a[j],a[j+1]);for(int i=0;i<n;i++)std::cout<<a[i]<<(i+1<n?" ":"");std::cout<<std::endl;}
""", [("5\n5 1 4 2 8\n", "1 2 4 5 8\n"), ("3\n-1 -5 0\n", "-5 -1 0\n"), ("1\n7\n", "7\n")], ["Arrays", "Sorting"]),
    _problem("Selection Sort", "Easy", "Read n followed by n integers. Sort them in non-decreasing order using selection sort and print them separated by spaces.", "5\n64 25 12 22 11", "11 12 22 25 64", r"""
#include <iostream>
#include <algorithm>
int main(){int n;std::cin>>n;long long a[200000];for(int i=0;i<n;i++)std::cin>>a[i];for(int i=0;i<n;i++){int m=i;for(int j=i+1;j<n;j++)if(a[j]<a[m])m=j;std::swap(a[i],a[m]);}for(int i=0;i<n;i++)std::cout<<a[i]<<(i+1<n?" ":"");std::cout<<std::endl;}
""", [("5\n64 25 12 22 11\n", "11 12 22 25 64\n"), ("3\n3 2 1\n", "1 2 3\n"), ("2\n-1 -1\n", "-1 -1\n")], ["Arrays", "Sorting"]),
    _problem("Matrix Trace", "Easy", "Read n followed by an n by n matrix of integers. Print the sum of its main diagonal.", "3\n1 2 3\n4 5 6\n7 8 9", "15", r"""
#include <iostream>
int main(){int n;std::cin>>n;long long x,s=0;for(int i=0;i<n;i++)for(int j=0;j<n;j++){std::cin>>x;if(i==j)s+=x;}std::cout<<s<<std::endl;}
""", [("3\n1 2 3\n4 5 6\n7 8 9\n", "15\n"), ("1\n-4\n", "-4\n"), ("2\n1 2\n3 4\n", "5\n")], ["Matrices", "Arrays"]),
    _problem("Matrix Row Sums", "Easy", "Read r and c followed by an r by c matrix. Print each row sum on its own line.", "2 3\n1 2 3\n4 5 6", "6\n15", r"""
#include <iostream>
int main(){int r,c;std::cin>>r>>c;long long x,s;for(int i=0;i<r;i++){s=0;for(int j=0;j<c;j++){std::cin>>x;s+=x;}std::cout<<s<<std::endl;}}
""", [("2 3\n1 2 3\n4 5 6\n", "6\n15\n"), ("1 2\n-1 5\n", "4\n"), ("2 1\n3\n-8\n", "3\n-8\n")], ["Matrices", "Arrays"]),
    _problem("Transpose a Matrix", "Easy", "Read r and c followed by an r by c matrix. Print its transpose as c rows, with values in each row separated by spaces.", "2 3\n1 2 3\n4 5 6", "1 4\n2 5\n3 6", r"""
#include <iostream>
int main(){int r,c;std::cin>>r>>c;long long a[500][500];for(int i=0;i<r;i++)for(int j=0;j<c;j++)std::cin>>a[i][j];for(int j=0;j<c;j++){for(int i=0;i<r;i++)std::cout<<a[i][j]<<(i+1<r?" ":"");std::cout<<std::endl;}}
""", [("2 3\n1 2 3\n4 5 6\n", "1 4\n2 5\n3 6\n"), ("1 2\n-2 7\n", "-2\n7\n"), ("2 1\n3\n9\n", "3 9\n")], ["Matrices", "Arrays"]),
    _problem("Count Consonants", "Easy", "Read one line and count English alphabetic characters that are not vowels. Ignore letter case; spaces, digits, and punctuation do not count.", "Code Streak 2026!", "6", r"""
#include <iostream>
#include <string>
#include <cctype>
int main(){std::string s;std::getline(std::cin,s);int n=0;for(char c:s){c=std::tolower((unsigned char)c);if(c>='a'&&c<='z'&&c!='a'&&c!='e'&&c!='i'&&c!='o'&&c!='u')n++;}std::cout<<n<<std::endl;}
""", [("Code Streak 2026!\n", "6\n"), ("AEIOU\n", "0\n"), ("xyz\n", "3\n")], ["Strings", "Counting"]),
    _problem("String Palindrome Check", "Easy", "Read one token and print YES if it is identical when reversed, otherwise print NO. Comparison is case-sensitive.", "level", "YES", r"""
#include <iostream>
#include <string>
int main(){std::string s;std::cin>>s;bool ok=true;for(int i=0,j=(int)s.size()-1;i<j;i++,j--)if(s[i]!=s[j])ok=false;std::cout<<(ok?"YES":"NO")<<std::endl;}
""", [("level\n", "YES\n"), ("Code\n", "NO\n"), ("a\n", "YES\n")], ["Strings", "Two Pointers"]),
    _problem("Reverse a String", "Easy", "Read one token and print its characters in reverse order.", "streak", "kaerts", r"""
#include <iostream>
#include <string>
#include <algorithm>
int main(){std::string s;std::cin>>s;std::reverse(s.begin(),s.end());std::cout<<s<<std::endl;}
""", [("streak\n", "kaerts\n"), ("a\n", "a\n"), ("abcd\n", "dcba\n")], ["Strings", "Reversal"]),
    _problem("Character Frequency", "Easy", "Read one token s and a character c. Print how many times c occurs in s.", "banana a", "3", r"""
#include <iostream>
#include <string>
int main(){std::string s;char c;std::cin>>s>>c;int n=0;for(char x:s)if(x==c)n++;std::cout<<n<<std::endl;}
""", [("banana a\n", "3\n"), ("hello z\n", "0\n"), ("aaaa a\n", "4\n")], ["Strings", "Counting"]),
    _problem("First Non-Repeating Character", "Easy", "Read one token and print its first character that occurs exactly once. Print -1 if every character repeats.", "swiss", "w", r"""
#include <iostream>
#include <string>
int main(){std::string s;std::cin>>s;for(char c:s){int n=0;for(char x:s)if(x==c)n++;if(n==1){std::cout<<c<<std::endl;return 0;}}std::cout<<-1<<std::endl;}
""", [("swiss\n", "w\n"), ("aabb\n", "-1\n"), ("abcd\n", "a\n")], ["Strings", "Hashing"]),
    _problem("Anagram Check", "Easy", "Read two lowercase alphabetic tokens. Print YES if they contain the same letters with the same frequencies, otherwise print NO.", "listen silent", "YES", r"""
#include <iostream>
#include <string>
#include <algorithm>
int main(){std::string a,b;std::cin>>a>>b;std::sort(a.begin(),a.end());std::sort(b.begin(),b.end());std::cout<<(a==b?"YES":"NO")<<std::endl;}
""", [("listen silent\n", "YES\n"), ("rat car\n", "NO\n"), ("a a\n", "YES\n")], ["Strings", "Sorting"]),
    _problem("Count Words", "Easy", "Read one full line and print the number of whitespace-separated words. Consecutive spaces do not create empty words.", "  code   streak practice ", "3", r"""
#include <iostream>
#include <sstream>
#include <string>
int main(){std::string s,w;std::getline(std::cin,s);std::stringstream ss(s);int n=0;while(ss>>w)n++;std::cout<<n<<std::endl;}
""", [("  code   streak practice \n", "3\n"), ("\n", "0\n"), ("one\n", "1\n")], ["Strings", "Parsing"]),
    _problem("Remove Spaces", "Easy", "Read one full line and print it with all space characters removed. Preserve every other character and its order.", "a b  c!", "abc!", r"""
#include <iostream>
#include <string>
int main(){std::string s;std::getline(std::cin,s);for(char c:s)if(c!=' ')std::cout<<c;std::cout<<std::endl;}
""", [("a b  c!\n", "abc!\n"), ("no spaces\n", "nospaces\n"), ("   \n", "\n")], ["Strings", "Filtering"]),
    _problem("Valid Parentheses", "Easy", "Read a string containing only (), [], and {}. Print YES if every opening bracket is closed by the same type in the correct order; otherwise print NO.", "{[()]}", "YES", r"""
#include <iostream>
#include <string>
#include <stack>
int main(){std::string s;std::cin>>s;std::stack<char> st;bool ok=true;for(char c:s){if(c=='('||c=='['||c=='{')st.push(c);else if(st.empty()||!((st.top()=='('&&c==')')||(st.top()=='['&&c==']')||(st.top()=='{'&&c=='}'))){ok=false;break;}else st.pop();}if(!st.empty())ok=false;std::cout<<(ok?"YES":"NO")<<std::endl;}
""", [("{[()]}\n", "YES\n"), ("([)]\n", "NO\n"), ("((\n", "NO\n")], ["Strings", "Stacks"]),
    _problem("Trailing Zeroes in Factorial", "Easy", "Read n (0 <= n <= 10^18) and print the number of trailing zeroes in n!.", "100", "24", r"""
#include <iostream>
int main(){long long n,s=0;std::cin>>n;while(n){n/=5;s+=n;}std::cout<<s<<std::endl;}
""", [("100\n", "24\n"), ("0\n", "0\n"), ("25\n", "6\n")], ["Math", "Number Theory"]),
    _problem("Binary to Decimal", "Easy", "Read a non-empty binary string and print its value as a base-10 integer. The value fits in signed 64-bit range.", "101101", "45", r"""
#include <iostream>
#include <string>
int main(){std::string s;std::cin>>s;long long n=0;for(char c:s)n=n*2+(c-'0');std::cout<<n<<std::endl;}
""", [("101101\n", "45\n"), ("0\n", "0\n"), ("1111\n", "15\n")], ["Math", "Number Systems"]),
    _problem("Decimal to Binary", "Easy", "Read a non-negative integer and print its binary representation without leading zeroes. Print 0 for input zero.", "13", "1101", r"""
#include <iostream>
#include <string>
#include <algorithm>
int main(){long long n;std::cin>>n;if(n==0){std::cout<<0<<std::endl;return 0;}std::string s;while(n){s.push_back('0'+n%2);n/=2;}std::reverse(s.begin(),s.end());std::cout<<s<<std::endl;}
""", [("13\n", "1101\n"), ("0\n", "0\n"), ("32\n", "100000\n")], ["Math", "Number Systems"]),
    _problem("Search Insert Position", "Easy", "Read n, a strictly increasing array of n integers, and target x. Print the index where x is found, or where it should be inserted to keep the array sorted. Indices are zero-based.", "4\n1 3 5 6\n2", "1", r"""
#include <iostream>
int main(){int n;std::cin>>n;long long a[200000],x;for(int i=0;i<n;i++)std::cin>>a[i];std::cin>>x;int l=0,r=n;while(l<r){int m=(l+r)/2;if(a[m]<x)l=m+1;else r=m;}std::cout<<l<<std::endl;}
""", [("4\n1 3 5 6\n2\n", "1\n"), ("4\n1 3 5 6\n7\n", "4\n"), ("3\n1 3 5\n1\n", "0\n")], ["Arrays", "Binary Search"]),
    _problem("Running Maximum", "Easy", "Read n followed by n integers. After each value, print the largest value seen so far. Print the n results separated by spaces.", "5\n2 1 5 3 6", "2 2 5 5 6", r"""
#include <iostream>
#include <climits>
int main(){int n;std::cin>>n;long long x,m=LLONG_MIN;for(int i=0;i<n;i++){std::cin>>x;if(x>m)m=x;std::cout<<m<<(i+1<n?" ":"");}std::cout<<std::endl;}
""", [("5\n2 1 5 3 6\n", "2 2 5 5 6\n"), ("3\n-4 -2 -8\n", "-4 -2 -2\n"), ("1\n7\n", "7\n")], ["Arrays", "Prefix Maximum"]),
    _problem("Count Positive Numbers", "Easy", "Read n followed by n integers and print how many are strictly greater than zero.", "6\n-1 0 4 9 -3 2", "3", r"""
#include <iostream>
int main(){int n,c=0;long long x;std::cin>>n;while(n--){std::cin>>x;if(x>0)c++;}std::cout<<c<<std::endl;}
""", [("6\n-1 0 4 9 -3 2\n", "3\n"), ("3\n0 -1 -2\n", "0\n"), ("2\n1 2\n", "2\n")], ["Arrays", "Counting"]),
)
