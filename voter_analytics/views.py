# views.py
# Name: Shuwei Zhu
# Email: david996@bu.edu
# Description: Views for voter analytics application including list, detail, and graph views

from django.views.generic import ListView, DetailView
from django.db.models import Q, Count
from .models import Voter
import plotly.graph_objs as go
import plotly.offline as pyo

class VoterListView(ListView):
    """
    View to display a paginated list of voters with filtering capabilities.
    
    Features:
    - Displays 100 voters per page
    - Supports filtering by party affiliation, birth year range, voter score, and voting history
    - Preserves filter selections when navigating between pages
    - Shows voter name, address, DOB, party affiliation, and voter score
    """
    model = Voter
    template_name = 'voter_analytics/voter_list.html'
    context_object_name = 'voters'
    paginate_by = 100
    
    def get_queryset(self):
        """
        Apply filters based on form input.
        
        Filters are applied cumulatively - if multiple filters are selected,
        voters must match ALL criteria (AND logic).
        
        Returns:
            QuerySet: Filtered voter records
        """
        queryset = super().get_queryset()
        
        # Get filter parameters
        party = self.request.GET.get('party_affiliation')
        min_dob_year = self.request.GET.get('min_dob_year')
        max_dob_year = self.request.GET.get('max_dob_year')
        voter_score = self.request.GET.get('voter_score')
        
        # Apply filters
        if party:
            queryset = queryset.filter(party_affiliation=party)
        
        if min_dob_year:
            queryset = queryset.filter(date_of_birth__year__gte=int(min_dob_year))
        
        if max_dob_year:
            queryset = queryset.filter(date_of_birth__year__lte=int(max_dob_year))
        
        if voter_score:
            queryset = queryset.filter(voter_score=int(voter_score))
        
        # Check for specific election filters
        if self.request.GET.get('v20state'):
            queryset = queryset.filter(v20state=True)
        if self.request.GET.get('v21town'):
            queryset = queryset.filter(v21town=True)
        if self.request.GET.get('v21primary'):
            queryset = queryset.filter(v21primary=True)
        if self.request.GET.get('v22general'):
            queryset = queryset.filter(v22general=True)
        if self.request.GET.get('v23town'):
            queryset = queryset.filter(v23town=True)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        Add filter form data to context.
        
        Provides data for dropdown menus and preserves user selections
        when filters are applied or when navigating between pages.
        
        Returns:
            dict: Context data including filter options and selected values
        """
        context = super().get_context_data(**kwargs)
        
        # Get distinct values for dropdowns
        context['parties'] = Voter.objects.values_list('party_affiliation', flat=True).distinct().order_by('party_affiliation')
        context['years'] = range(1900, 2025)
        context['voter_scores'] = range(6)
        
        # Preserve filter values
        context['selected_party'] = self.request.GET.get('party_affiliation', '')
        context['selected_min_year'] = self.request.GET.get('min_dob_year', '')
        context['selected_max_year'] = self.request.GET.get('max_dob_year', '')
        context['selected_voter_score'] = self.request.GET.get('voter_score', '')
        context['v20state_checked'] = 'v20state' in self.request.GET
        context['v21town_checked'] = 'v21town' in self.request.GET
        context['v21primary_checked'] = 'v21primary' in self.request.GET
        context['v22general_checked'] = 'v22general' in self.request.GET
        context['v23town_checked'] = 'v23town' in self.request.GET
        
        return context


class VoterDetailView(DetailView):
    """
    View to display detailed information about a single voter.
    
    Shows all voter fields including:
    - Personal information (name, DOB, party affiliation)
    - Address details with Google Maps integration
    - Complete voting history for all 5 elections
    - Registration date and precinct information
    """
    model = Voter
    template_name = 'voter_analytics/voter_detail.html'
    context_object_name = 'voter'


class VoterGraphsView(ListView):
    """
    View to display graphs analyzing voter data with filtering capabilities.
    
    Creates three interactive Plotly graphs:
    1. Histogram of voter distribution by birth year
    2. Pie chart of voter distribution by party affiliation
    3. Bar chart of voter participation by election
    
    Uses the same filtering system as VoterListView to allow
    analysis of specific voter segments.
    """
    model = Voter
    template_name = 'voter_analytics/graphs.html'
    context_object_name = 'voters'
    
    def get_queryset(self):
        """Apply filters based on form input (same as VoterListView)"""
        queryset = super().get_queryset()
        
        # Get filter parameters
        party = self.request.GET.get('party_affiliation')
        min_dob_year = self.request.GET.get('min_dob_year')
        max_dob_year = self.request.GET.get('max_dob_year')
        voter_score = self.request.GET.get('voter_score')
        
        # Apply filters
        if party:
            queryset = queryset.filter(party_affiliation=party)
        
        if min_dob_year:
            queryset = queryset.filter(date_of_birth__year__gte=int(min_dob_year))
        
        if max_dob_year:
            queryset = queryset.filter(date_of_birth__year__lte=int(max_dob_year))
        
        if voter_score:
            queryset = queryset.filter(voter_score=int(voter_score))
        
        # Check for specific election filters
        if self.request.GET.get('v20state'):
            queryset = queryset.filter(v20state=True)
        if self.request.GET.get('v21town'):
            queryset = queryset.filter(v21town=True)
        if self.request.GET.get('v21primary'):
            queryset = queryset.filter(v21primary=True)
        if self.request.GET.get('v22general'):
            queryset = queryset.filter(v22general=True)
        if self.request.GET.get('v23town'):
            queryset = queryset.filter(v23town=True)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        Generate graphs and add to context.
        
        Creates three graphs based on the filtered voter data and adds
        them to the template context as HTML div elements. Also includes
        filter form data to maintain consistency with the list view.
        
        Returns:
            dict: Context data including graph HTML and filter options
        """
        context = super().get_context_data(**kwargs)
        
        # Get filtered queryset
        voters = self.get_queryset()
        
        # Create graphs
        context['birth_year_graph'] = self.create_birth_year_histogram(voters)
        context['party_graph'] = self.create_party_pie_chart(voters)
        context['election_graph'] = self.create_election_histogram(voters)
        
        # Add filter form data
        context['parties'] = Voter.objects.values_list('party_affiliation', flat=True).distinct().order_by('party_affiliation')
        context['years'] = range(1900, 2025)
        context['voter_scores'] = range(6)
        
        # Preserve filter values
        context['selected_party'] = self.request.GET.get('party_affiliation', '')
        context['selected_min_year'] = self.request.GET.get('min_dob_year', '')
        context['selected_max_year'] = self.request.GET.get('max_dob_year', '')
        context['selected_voter_score'] = self.request.GET.get('voter_score', '')
        context['v20state_checked'] = 'v20state' in self.request.GET
        context['v21town_checked'] = 'v21town' in self.request.GET
        context['v21primary_checked'] = 'v21primary' in self.request.GET
        context['v22general_checked'] = 'v22general' in self.request.GET
        context['v23town_checked'] = 'v23town' in self.request.GET
        
        return context
    
    def create_birth_year_histogram(self, voters):
        """
        Create histogram of voter distribution by birth year.
        
        Args:
            voters (QuerySet): Filtered voter records
            
        Returns:
            str: HTML div containing the Plotly histogram
        """
        # Get birth year counts
        birth_years = voters.values_list('date_of_birth__year', flat=True)
        year_counts = {}
        for year in birth_years:
            year_counts[year] = year_counts.get(year, 0) + 1
        
        # Sort years
        sorted_years = sorted(year_counts.keys())
        
        # Create histogram
        fig = go.Figure(data=[
            go.Bar(
                x=sorted_years,
                y=[year_counts[year] for year in sorted_years],
                marker_color='rgb(55, 83, 251)'
            )
        ])
        
        fig.update_layout(
            title=f'Voter distribution by Year of Birth (n={len(voters)})',
            xaxis_title='Year of Birth',
            yaxis_title='Number of Voters',
            showlegend=False,
            height=500
        )
        
        return pyo.plot(fig, output_type='div', include_plotlyjs=False)
    
    def create_party_pie_chart(self, voters):
        """
        Create pie chart of voter distribution by party affiliation.
        
        Shows the percentage breakdown of voters by party, useful for
        understanding the political composition of the filtered voter set.
        
        Args:
            voters (QuerySet): Filtered voter records
            
        Returns:
            str: HTML div containing the Plotly pie chart
        """
        # Get party counts
        party_counts = voters.values('party_affiliation').annotate(count=Count('id')).order_by('-count')
        
        labels = []
        values = []
        for item in party_counts:
            labels.append(item['party_affiliation'])
            values.append(item['count'])
        
        # Create pie chart
        fig = go.Figure(data=[
            go.Pie(
                labels=labels,
                values=values,
                textinfo='label+percent',
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title=f'Voter distribution by Party Affiliation (n={len(voters)})',
            height=500
        )
        
        return pyo.plot(fig, output_type='div', include_plotlyjs=False)
    
    def create_election_histogram(self, voters):
        """
        Create histogram of voter participation by election.
        
        Shows how many voters participated in each of the 5 elections,
        helping identify which elections had higher turnout among the
        filtered voter group.
        
        Args:
            voters (QuerySet): Filtered voter records
            
        Returns:
            str: HTML div containing the Plotly bar chart
        """
        # Count participation in each election
        election_data = {
            'v20state': voters.filter(v20state=True).count(),
            'v21town': voters.filter(v21town=True).count(),
            'v21primary': voters.filter(v21primary=True).count(),
            'v22general': voters.filter(v22general=True).count(),
            'v23town': voters.filter(v23town=True).count()
        }
        
        # Create histogram
        fig = go.Figure(data=[
            go.Bar(
                x=list(election_data.keys()),
                y=list(election_data.values()),
                marker_color='rgb(55, 83, 251)'
            )
        ])
        
        fig.update_layout(
            title=f'Vote Count by Election (n={len(voters)})',
            xaxis_title='Election',
            yaxis_title='Number of Voters',
            showlegend=False,
            height=500
        )
        
        return pyo.plot(fig, output_type='div', include_plotlyjs=False)