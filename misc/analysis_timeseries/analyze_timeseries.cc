/* C. Lechner, 2025-Nov */
#include <iostream>
#include <fstream>
#include <vector>
#include <algorithm>
#include <iomanip>

using namespace std;

struct ele {
	double d;
	int len {0};
};

const double max_deltat = 900.;

int main(int argc, char *argv[])
{
	if(argc!=2) {
		cerr << "This program requires one argument: the name of the CSV file to analyze" << endl;
		exit(1);
	}

	const string fn(argv[1]);
	ifstream fin(fn, ios::in);
	vector<struct ele> data;

	if (!fin.is_open()) {
		cerr << "could not open input file " << fn << endl;
		exit(1);
	}

	double tmp = 0.0;
	while(fin >> tmp) {
		struct ele q;
		q.d = tmp;
		data.push_back(q);
	}

	// sort in ASCENDING timestamp order
	sort(
		data.begin(), data.end(),
		[](struct ele a, struct ele b) { return(a.d<b.d /* defines sort order */ ); }
	);

	cout << "size of data loaded from file=" << data.size() << endl;

	int kk=0;
	int max_len=-1;
	auto it_max = data.begin();
	auto it_later = data.begin();
	for(auto it_earlier=data.begin(); it_earlier!=data.end(); ++it_earlier)
	{
		for( ; it_later!=data.end() ; ) {
			// look ahead: check if next element would still meet criterion
			auto it_later_next = (it_later+1);
			if  ( (it_later_next!=data.end())
			   && (it_later_next->d-it_earlier->d)<max_deltat) {
				// not yet there -> proceed with loop
				it_later = it_later_next;
				continue;
			}
			break;
		}

		int curr_len = 1+distance(it_earlier,it_later); // "1+" because if both iterators point to identical element we consider it a series of length 1
		it_earlier->len = curr_len;
		if (curr_len>max_len) {
			max_len = curr_len;
			it_max = it_earlier;
		}


#if 0
		cout << fixed << it_earlier->d << " -> "  << it_later->d << " deltat=" << it_later->d-it_earlier->d << " #ele=" << curr_len << endl;
		if(kk>5)
			break;
		kk++;
#endif
	}

	cout << "Longest burst of events with duration " << max_deltat << " begins at" << endl;
	cout << "t0=" << fixed << it_max->d << ", len=" << it_max->len << endl;

	return(0);
}
