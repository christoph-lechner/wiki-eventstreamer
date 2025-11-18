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

int main(void)
{
	ifstream fin("output.csv", ios::in);
	vector<struct ele> data;

	if (!fin.is_open()) {
		cerr << "could not open input file" << endl;
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

	int max_len=-1;
	int kk=0;
	auto it_later = data.begin();
	// FIXME: iterator end condition should be done using !=
	for(auto it_earlier=data.begin(); it_earlier!=data.end(); ++it_earlier)
	{
#if 1
		// FIXME: would need to "look ahead" -> check that next element is still below deltat=900s
		for( ; it_later<data.end() && (it_later->d-it_earlier->d)<900.; ++it_later)
			;
#endif

		int curr_len = distance(it_earlier,it_later);
		it_earlier->len = curr_len;
		max_len = (max_len>curr_len) ? max_len : curr_len;

#if 0
		cout << fixed << it_earlier->d << " -> "  << it_later->d << " deltat=" << it_later->d-it_earlier->d << " #ele=" << curr_len << endl;
		if(kk>5)
			break;
		kk++;
#endif
	}

	cout << "maxlen=" << max_len << endl;

	return(0);
}
